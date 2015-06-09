import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class Device(models.Model):
    # Device types
    COMPUTER = 'computer'
    MOBILE = 'mobile'
    MONITOR = 'monitor'
    PERIPHERAL = 'peripheral'
    TYPES = (
        (COMPUTER, 'computer'),
        (MOBILE, 'mobile'),
        (MONITOR, 'monitor'),
        (PERIPHERAL, 'peripheral'),
    )
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    # id is an arbitrary identifier generated by the agent
    id = models.CharField('Identifier provided by the agent.', max_length=128)
    # hardware identifier can be obtained by anyone
    # XXX mark hid as unique=True?
    hid = models.CharField('Hardware identifier.', max_length=32)
    type = models.CharField(max_length=16, choices=TYPES)
    # XXX is_id_secured & ituuid
    
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
        for e in self.events.filter(Q(type=Event.ADD) | Q(type=Event.REMOVE)):
            if e.type == Event.ADD:
                components += e.components.all()
            else:  # Event.REMOVE
                components = list(set(components) - set(e.components.all()))
        
        return components
    
    @property
    def parent(self):
        # Compute events that modify relation between devices.
        RELATION_EVENTS = [Event.REGISTER, Event.ADD, Event.REMOVE]
        try:
            event = self.parent_events.filter(type__in=RELATION_EVENTS).latest()
        except Event.DoesNotExist:
            return None
        
        if event.type == Event.REMOVE:
            return None
        
        return event.device


class EventManager(models.Manager):
    def related_to_device(self, device):
        return self.filter(Q(device=device) | Q(components__in=[device]))


class Event(models.Model):
    # initial events (iteration 1)
    REGISTER = 'register'
    RECYCLE = 'recycle'
    
    # base events (iteration 2)
    USE = 'use'
    TRANSFER = 'transfer'
    COLLECT = 'collect'
    
    # extended events (iteration 3)
    DEREGISTER = 'deregister'
    LOCATE = 'locate'
    ADD = 'add'
    REMOVE = 'remove'
    SNAPSHOT = 'snapshot'
    MIGRATE = 'migrate'
    INCIDENCE = 'incidence'
    
    TYPES = (
        (REGISTER, 'REGISTER'),
        # (USE, 'USE'),
        # (TRANSFER, 'TRANSFER'),
        (COLLECT, 'COLLECT'),
        (RECYCLE, 'RECYCLE'),
        (ADD, 'ADD'),
        (REMOVE, 'REMOVE'),
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=16, choices=TYPES)
    data = models.TextField()  # Use PostgreSQL HStore field?
    # https://docs.djangoproject.com/en/1.8/ref/contrib/postgres/fields/#hstorefield
    
    event_time = models.DateTimeField('Time when the event has happened.')
    by_user = models.CharField('User who performs the event.', max_length=32)
    
    agent = models.ForeignKey('Agent', related_name='+')
    device = models.ForeignKey('Device', related_name='events')
    components = models.ManyToManyField('Device', related_name='parent_events')
    
    objects = EventManager()
    
    class Meta:
        get_latest_by = 'timestamp'
    
    def __str__(self):
        event_date = self.timestamp.strftime("%Y-%m-%d")
        return "%s %s %s" % (self.agent, self.type, event_date)


class Agent(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField()
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    
    def __str__(self):
        return self.name
