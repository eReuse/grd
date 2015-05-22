import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models import Q
from django.utils import timezone


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
        # (USE, 'USE'),
        # (TRANSFER, 'TRANSFER'),
        # (COLLECT, 'COLLECT'),
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
    # XXX mark hid as unique=True?
    hid = models.CharField('Hardware identifier.', max_length=32)
    type = models.CharField(max_length=16, choices=TYPES)
    # XXX is_id_secured & ituuid
    
    @property
    def components(self):
        last_log = self.logs.filter(event='register').latest()
        return last_log.components.all()


class EntryLogManager(models.Manager):
    def related_to_device(self, device):
        return self.filter(Q(device=device) | Q(components__in=[device]))


class EntryLog(models.Model):
    class Meta:
        get_latest_by = 'timestamp'
    
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length=16, choices=Device.EVENTS)
    data = models.TextField()  # Use PostgreSQL HStore field?
    # https://docs.djangoproject.com/en/1.8/ref/contrib/postgres/fields/#hstorefield
    
    event_time = models.DateTimeField('Time when the event has happened.')
    by_user = models.CharField('User who performs the event.', max_length=32)
    
    agent = models.ForeignKey('Agent', related_name='+')
    device = models.ForeignKey('Device', related_name='logs')
    components = models.ManyToManyField('Device', related_name='parent_logs')
    
    objects = EntryLogManager()


class Agent(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField()


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    Describes a user who belongs to an Agent.
    
    The implementation is based on auth.models.AbstractBaseUser, more:
    https://docs.djangoproject.com/en/dev/topics/auth/#customizing-the-user-model
    """
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as '
                  'active. Unselect this instead of deleting accounts.')
    is_admin = models.BooleanField(
        default=False,
        help_text='Designates that this user has all permissions without '
                  'explicitly assigning them.')
    date_joined = models.DateTimeField(default=timezone.now)
    agent = models.ForeignKey('Agent', null=True, related_name='users')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def get_full_name(self):
        # The user is identified by their email address
        return self.email
    
    def get_short_name(self):
        # The user is identified by their email address
        return self.email
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
    
    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


# class Event(models.Model):
    # TODO(v0.2) CRUD events
    #  https://www.wrike.com/open.htm?id=47864028
