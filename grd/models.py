import uuid

from django.db import models


class Device(models.Model):
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
    
    EVENTS = (
        (REGISTER, 'REGISTER'),
#        (USE, 'USE'),
#        (TRANSFER, 'TRANSFER'),
#        (COLLECT, 'COLLECT'),
        (RECYCLE, 'RECYCLE'),
    )
    
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
    id = models.CharField('Identifier provided by the agent.', max_length=128)
    hid = models.CharField('Hardware identifier.', max_length=32)
    type = models.CharField(max_length=16, choices=TYPES)
    # XXX is_id_secured & ituuid
    
    #logs = models.ManyToManyField()#"self", throught
    #https://docs.djangoproject.com/en/1.8/ref/models/fields/#django.db.models.ManyToManyField.through


class EntryLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length='16', choices=Device.EVENTS)
    data = models.TextField() # Use PostgreSQL HStore field?
    # https://docs.djangoproject.com/en/1.8/ref/contrib/postgres/fields/#hstorefield
    
    event_time = models.DateTimeField('Time when the event has happened.')
    by_user = models.CharField('User who performs the event.', max_length='32')
    
    agent = models.ForeignKey('Agent', related_name='+')
    device = models.ForeignKey('Device', related_name='logs')
    components = models.ManyToManyField('Device', related_name='parent_logs')


class Agent(models.Model):
    name = models.CharField(max_length='128', unique=True)
    description = models.TextField()


#class Event(models.Model):
    #TODO(v0.2) CRUD events
    # https://www.wrike.com/open.htm?id=47864028
