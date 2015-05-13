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
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                            editable=False)
    id = models.CharField('Device identifier provided by the agent.',
                          max_length=32)
    # http://journalseeker.researchbib.com/?action=issnChecker
    
    #logs = models.ManyToManyField()#"self", throught
    #https://docs.djangoproject.com/en/1.8/ref/models/fields/#django.db.models.ManyToManyField.through


class EntryLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length='16', choices=Device.EVENTS)
    data = models.TextField() # Use PostgreSQL HStore field?
    # https://docs.djangoproject.com/en/1.8/ref/contrib/postgres/fields/#hstorefield
    agent = models.ForeignKey('Agent', related_name='logs')
    device = models.ForeignKey('Device', related_name='logs')


class Agent(models.Model):
    name = models.CharField(max_length='128')
    description = models.TextField()


#class Event(models.Model):
    #TODO(v0.2) CRUD events
    # https://www.wrike.com/open.htm?id=47864028
