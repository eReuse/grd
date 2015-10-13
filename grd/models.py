from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import HStoreField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Device(models.Model):
    # Device types
    COMPUTER = 'Computer'
    LAPTOP = 'Laptop'
    MOBILE = 'Mobile'
    MONITOR = 'Monitor'
    PERIPHERAL = 'Peripheral'
    TYPES = (
        (COMPUTER, 'computer'),
        (LAPTOP, 'laptop'),
        (MOBILE, 'mobile'),
        (MONITOR, 'monitor'),
        (PERIPHERAL, 'peripheral'),
    )
    
    sameAs = models.URLField('URI provided by the agent.')
    # hardware identifier can be obtained by anyone
    # TODO define some kind of validation to HID (shold be slugizable)
    hid = models.CharField('Hardware identifier.', primary_key=True,
                           max_length=128)  # FIXME how long can be hid?
    type = models.CharField(max_length=16, choices=TYPES)
    productionDate = models.DateField(null=True)
    
    def __str__(self):
        return "%s %s" % (self.type, self.pk)
    
    @property
    def components(self):
        try:
            # Get the latest register event (can exist several because
            # of snapshots)
            last_event = self.events.filter(type=Event.REGISTER).latest()
        except Event.DoesNotExist:
            # Device has been registered as component of another Device
            # so it doesn't have a registered event.
            components = []
        else:
            components = list(last_event.components.all())
        
        # Compute add and remove events. Get add and remove together
        # because the order of the operations affects the final result.
        for e in self.events.filter(type__in=[Event.ADD, Event.REMOVE]):
            if e.type == Event.ADD:
                components += e.components.all()
            else:  # Event.REMOVE
                components = list(set(components) - set(e.components.all()))
        
        return components
    
    @property
    def holder(self):
        try:
            last_migration = self.events.filter(type=Event.MIGRATE).latest()
        except Event.DoesNotExist:
            pass
        else:
            return Agent.objects.get(pk=last_migration.to)
        
        # There is no migrations, so find which agent registered the device
        try:
            # Get the latest register event (can exist several because
            # of snapshots)
            last_event = self.events.filter(type=Event.REGISTER).latest()
        except Event.DoesNotExist:
            # Device has been registered as component of another Device
            # so it doesn't have a registered event.
            # TODO inherit owner from parent device
            raise NotImplementedError
            owner = None
        else:
            owner = last_event.agent
        return owner
    
    @property
    def owners(self):
        ASSIGNATION_EVENTS = [Event.ALLOCATE, Event.DEALLOCATE]
        
        # Compute allocate and deallocate events. Get both together
        # because the order of the operations affects the final result.
        device_owners = []
        for e in self.events.filter(type__in=ASSIGNATION_EVENTS):
            if e.type == Event.ALLOCATE:
                device_owners.append(e.owner.url)
            else:  # Event.DEALLOCATE
                device_owners.remove(e.owner.url)
        
        return device_owners
    
    @property
    def parent(self):
        # Compute events that modify relation between devices.
        DEV_REL_EVENTS = [Event.REGISTER, Event.ADD, Event.REMOVE]
        try:
            event = self.parent_events.filter(type__in=DEV_REL_EVENTS).latest()
        except Event.DoesNotExist:
            return None
        
        if event.type == Event.REMOVE:
            return None
        
        return event.device
    
    @property
    def running_time(self):
        USAGE_EVENTS = [Event.USAGEPROOF, Event.STOPUSAGE]
        qs = self.events.filter(type__in=USAGE_EVENTS)
        
        # the device has not been used
        if not qs.filter(type=Event.USAGEPROOF).exists():
            return 0
        
        beg_date = None
        seconds = 0
        for e in qs:
            if e.type == Event.USAGEPROOF:
                beg_date = e.date
            
            elif e.type == Event.STOPUSAGE:
                seconds += (e.date - beg_date).total_seconds()
                beg_date = None

        if beg_date is not None:
            # There is no StopUsage event: is the device currently on use?
            # TODO(santiago) which kind of events means that the device
            # is not being used anymore?
            try:
                end_date = self.events.get(type=Event.RECYCLE).date
            except Event.DoesNotExist:
                end_date = timezone.now()
            seconds += (end_date - beg_date).total_seconds()
        
        return seconds


class EventManager(models.Manager):
    def related_to_device(self, device):
        return self.filter(Q(device=device) | Q(components__in=[device]))


class Event(models.Model):
    # Administrative (affects resposible agent)
    REGISTER = 'Register'
    LOCATE = 'Locate'
    MIGRATE = 'Migrate'
    RECYCLE = 'Recycle'
    
    # Users (logging purposes)
    ALLOCATE = 'Allocate'
    DEALLOCATE = 'Deallocate'
    RECEIVE = 'Receive'
    USAGEPROOF = 'UsageProof'
    STOPUSAGE = 'StopUsage'
    
    # Device interrelationships
    ADD = 'Add'
    REMOVE = 'Remove'
    
    TYPES = (
        (ADD, 'ADD'),
        (ALLOCATE, 'ALLOCATE'),
        (DEALLOCATE, 'DEALLOCATE'),
        (LOCATE, 'LOCATE'),
        (MIGRATE, 'MIGRATE'),
        (REGISTER, 'REGISTER'),
        (RECEIVE, 'RECEIVE'),
        (RECYCLE, 'RECYCLE'),
        (REMOVE, 'REMOVE'),
        (STOPUSAGE, 'STOPUSAGE'),
        (USAGEPROOF, 'USAGEPROOF'),
    )
    
    type = models.CharField(max_length=16, choices=TYPES)
    date = models.DateTimeField('Time when the event has happened.')
    grdTimestamp = models.DateTimeField(auto_now_add=True)
    # TODO replace with AgentUser
    byUser = models.CharField('User who performs the event.', max_length=128)
    
    agent = models.ForeignKey('Agent', related_name='+')
    device = models.ForeignKey('Device', related_name='events')
    components = models.ManyToManyField('Device', related_name='parent_events')
    
    # Allocate/Deallocate Event attributes
    owner = models.ForeignKey('AgentUser', null=True)
    
    data = HStoreField(default={})  # A field for storing mappings of strings to strings.
    
    objects = EventManager()
    
    class Meta:
        get_latest_by = 'grdTimestamp'
        # WARNING: the order of the events affects the computation of
        # the device's state, so be sure that you know what are you
        # doing before changing this field.
        ordering = ['grdTimestamp']
    
    def __str__(self):
        event_date = self.grdTimestamp.strftime("%Y-%m-%d")
        return "%s %s %s" % (self.agent, self.type, event_date)
    
    @property
    def to(self):
        # TODO return an agent instance instead a string?
        # agent_pk = self.data.get('to', None)
        # if agent_pk is not None:
        #     return Agent.objects.get(pk=agent_pk)
        # return None
        return self.data.get('to', None)


class Agent(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField()
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('agent-detail', args=[self.pk])


class AgentUser(models.Model):
    url = models.URLField('URL pointing to an User or an Organization.',
                          max_length=128, unique=True)
    
    def __str__(self):
        return self.url


class Location(gis_models.Model):
    # NOTE default spatial reference system for geometry fields is WGS84
    lat = models.FloatField()
    lon = models.FloatField()
    
    event = models.OneToOneField('Event', primary_key=True)
    
    objects = gis_models.GeoManager()
    
    def __str__(self):
        return self.label
