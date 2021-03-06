from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from grd.models import Agent, Device, Event


User = get_user_model()

# TODO: encapsulate fixtures for each TestCase to help readability

class DeviceTest(TestCase):
    """
    There are two devices: one and two.
    There are not relation between the devices.
    
    """
    fixtures = ['agents.json', 'devices.json', 'events_register.json',
                'users.json']
    
    def setUp(self):
        super(DeviceTest, self).setUp()
        self.device_one = Device.objects.get(hid="XPS13-1111-2222")
        self.device_two = Device.objects.get(hid="LED24-Acme-44")
    
    def test_get_components_device_with_register_event(self):
        device = Device.objects.get(hid="XPS13-1111-2222")
        self.assertEqual([], list(device.components))
    
    def test_get_parent_add(self):
        event = Event.objects.create(
            agent=Agent.objects.first(),
            device=self.device_one,
            type=Event.ADD,
            date=timezone.now(),
            dhDate=timezone.now(),
            byUser='http://example.org/users/XSR',
        )
        event.components.add(self.device_two)
        self.assertEqual(self.device_two.parent, self.device_one)


class ComponentsTest(TestCase):
    """
    There are two devices: one and two.
    Device two is a component of device one.
    
    """
    
    fixtures = ['agents.json', 'devices.json', 'events.json', 'users.json']
    
    def setUp(self):
        super(ComponentsTest, self).setUp()
        self.device_one = Device.objects.get(hid="XPS13-1111-2222")
        self.device_two = Device.objects.get(hid="LED24-Acme-44")
    
    def test_get_components_device_without_register_event(self):
        # Device has registered as component so inherits register
        device = Device.objects.get(hid="LED24-Acme-44")
        self.assertEqual([], list(device.components))
    
    def test_get_parent(self):
        self.assertEqual(self.device_one, self.device_two.parent)
        self.assertIsNone(self.device_one.parent)
    
    def test_get_parent_remove(self):
        event = Event.objects.create(
            agent=Agent.objects.first(),
            device=self.device_one,
            type=Event.REMOVE,
            date=timezone.now(),
            dhDate=timezone.now(),
            byUser='http://example.org/users/XSR',
        )
        event.components.add(self.device_two)
        self.assertIsNone(self.device_two.parent)


class HolderTest(TestCase):
    def setUp(self):
        super(HolderTest, self).setUp()
        u = User.objects.create_user("nikolao", "nikolao@example.org", "secret")
        self.agent = Agent.objects.create(name="Ahoth", user=u)
        u2 = User.objects.create_user("cayden", "cayden@example.org", "secret")
        self.agent2 = Agent.objects.create(name="Susumu", user=u2)

    def register_device(self):
        device = Device.objects.create(hid="1234", type=Device.COMPUTER,
                                       sameAs="http://example.org/device/1234/")
        device.events.create(
            agent=self.agent,
            type=Event.REGISTER,
            date="2015-09-08T12:38:20.604Z",
            dhDate="2015-09-18T12:38:20.604Z",
            byUser="http://example.org/users/foo"
        )
        return device
    
    def migrate_device(self, device, to):
        device.events.create(
            agent=self.agent,
            type=Event.MIGRATE,
            date="2015-09-08T12:58:20.604Z",
            dhDate="2015-09-08T12:58:20.604Z",
            byUser="http://example.org/users/foo",
            data={'to': str(self.agent2.pk)}
        )
    
    def test_holder(self):
        device = self.register_device()
        self.assertEqual(device.holder, self.agent)
    
    def test_holder_after_migration(self):
        device = self.register_device()
        self.migrate_device(device, self.agent2)
        self.assertEqual(device.holder, self.agent2)
    
    # TODO test_holder_of_component


class RunningTimeTest(TestCase):
    def setUp(self):
        super(RunningTimeTest, self).setUp()
        u = User.objects.create_user("nikolao", "nikolao@example.org", "secret")
        self.agent = Agent.objects.create(name="Ahoth", user=u)
        device = Device.objects.create(hid="1234", type=Device.COMPUTER,
                                       sameAs="http://example.org/device/1234/")
        device.events.create(
            agent=self.agent,
            type=Event.REGISTER,
            date="2015-09-08T12:38:20.604Z",
            dhDate="2015-09-09T12:38:20.604Z",
            byUser="http://example.org/users/foo"
        )
        self.device = device
    
    def test_no_use_reported(self):
        device = self.device
        self.assertEqual(0, device.running_time)
    
    def test_single_use_reported(self):
        device = self.device
        device.events.create(
            agent=self.agent,
            type=Event.USAGEPROOF,
            date="2015-09-08T12:38:20.604Z",
            dhDate="2015-09-09T12:38:20.604Z",
            byUser="http://example.org/users/foo"
        )
        device.events.create(
            agent=self.agent,
            type=Event.STOPUSAGE,
            date="2015-09-08T12:38:45.604Z",
            dhDate="2015-09-09T12:38:45.604Z",
            byUser="http://example.org/users/foo"
        )
        self.assertEqual(25, device.running_time)
    
    def test_currently_on_use(self):  # There isn't final event
        device = self.device
        time_on_use = timedelta(hours=12)
        usage_date = timezone.now() - time_on_use
        device.events.create(
            agent=self.agent,
            type=Event.USAGEPROOF,
            date=usage_date,
            dhDate=usage_date,
            byUser="http://example.org/users/foo"
        )
        # NOTE round timedelta to allow some difference because of
        # time spent on computation.
        self.assertEqual(time_on_use.total_seconds(),
                         round(device.running_time, -1))
    
    def test_several_uses_reported(self):
        device = self.device
        # device was used for a couple of hours
        device.events.create(
            agent=self.agent,
            type=Event.USAGEPROOF,
            date="2015-09-08T12:00:00.604Z",
            dhDate="2015-09-09T12:00:00.604Z",
            byUser="http://example.org/users/foo"
        )
        device.events.create(
            agent=self.agent,
            type=Event.STOPUSAGE,
            date="2015-09-08T14:00:00.604Z",
            dhDate="2015-09-08T16:00:00.604Z",
            byUser="http://example.org/users/foo"
        )
        # device was used for a couple of hours more
        device.events.create(
            agent=self.agent,
            type=Event.USAGEPROOF,
            date="2015-09-10T12:00:00.604Z",
            dhDate="2015-09-10T12:00:00.604Z",
            byUser="http://example.org/users/foo"
        )
        device.events.create(
            agent=self.agent,
            type=Event.STOPUSAGE,
            date="2015-09-10T14:00:00.604Z",
            dhDate="2015-09-10T14:00:00.604Z",
            byUser="http://example.org/users/foo"
        )
        
        self.assertEqual(4 * 3600, device.running_time)
    
    def test_device_recycled_but_stop_usage_unreported(self):
        device = self.device
        device.events.create(
            agent=self.agent,
            type=Event.USAGEPROOF,
            date="2015-09-08T12:38:20.604Z",
            dhDate="2015-09-08T12:38:20.604Z",            
            byUser="http://example.org/users/foo"
        )
        device.events.create(
            agent=self.agent,
            type=Event.RECYCLE,
            date="2015-09-08T12:38:45.604Z",
            dhDate="2015-09-08T12:38:45.604Z",
            byUser="http://example.org/users/foo"
        )
        self.assertEqual(25, device.running_time)


class DurabilityTest(TestCase):
    def setUp(self):
        super(DurabilityTest, self).setUp()
        u = User.objects.create_user("nikolao", "nikolao@example.org", "secret")
        self.agent = Agent.objects.create(name="Ahoth", user=u)
        device = Device.objects.create(hid="1234", type=Device.COMPUTER,
                                       sameAs="http://example.org/device/1234/")
        device.events.create(
            agent=self.agent,
            type=Event.REGISTER,
            date="2014-01-01T00:00:00.000Z",
            dhDate="2014-01-20T00:00:00.000Z",
            byUser="http://example.org/users/foo"
        )
        self.device = device
    
    def test_device_with_production_date(self):
        device = self.device
        device.productionDate = date(2009, 1, 1)
        device.save()
        
        recycled_on = "2015-01-01T00:00:00.000Z"
        device.events.create(
            agent=self.agent,
            type=Event.RECYCLE,
            date=recycled_on,
            dhDate="2015-01-21T00:00:00.000Z",
            byUser="http://example.org/users/foo"
        )
        
        self.assertEqual(device.durability, 6)
    
    def test_device_without_production_date(self):
        device = self.device
        recycled_on = "2015-01-01T00:00:00.000Z"
        device.events.create(
            agent=self.agent,
            type=Event.RECYCLE,
            date=recycled_on,
            dhDate="2015-01-21T00:00:00.000Z",
            byUser="http://example.org/users/foo"
        )
        
        self.assertEqual(device.durability, 1)
    
    def test_device_without_production_date_several_register_events(self):
        device = self.device
        device.events.create(
            agent=self.agent,
            type=Event.REGISTER,
            date="2014-01-01T00:00:00.000Z",
            dhDate="2014-02-01T00:00:00.000Z",
            byUser="http://example.org/users/foo"
        )
        recycled_on = "2015-01-01T00:00:00.000Z"
        device.events.create(
            agent=self.agent,
            type=Event.RECYCLE,
            date=recycled_on,
            dhDate = "2015-01-01T02:00:00.000Z",
            byUser="http://example.org/users/foo"
        )
        self.assertEqual(device.durability, 1)
    
    def test_device_not_recycled(self):
        with self.assertRaises(ValueError):
            self.device.durability
