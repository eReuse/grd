from django.test import TestCase
from django.utils import timezone
from grd.models import Agent, Device, Event


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
        self.device_two = Device.objects.get(hid="DDR3")
    
    def test_get_components_device_with_register_event(self):
        device = Device.objects.get(hid="XPS13-1111-2222")
        self.assertEqual([], list(device.components))
    
    def test_get_parent_add(self):
        event = Event.objects.create(
            agent=Agent.objects.first(),
            device=self.device_one,
            type=Event.ADD,
            date=timezone.now(),
            byUser='XSR',
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
        self.device_two = Device.objects.get(hid="DDR3")
    
    def test_get_components_device_without_register_event(self):
        # Device has registered as component so inherits register
        device = Device.objects.get(hid="DDR3")
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
            byUser='XSR',
        )
        event.components.add(self.device_two)
        self.assertIsNone(self.device_two.parent)
