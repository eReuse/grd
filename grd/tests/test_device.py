from django.test import TestCase
from grd.models import Device


# TODO: encapsulate fixtures for each TestCase to help readability

class DeviceTest(TestCase):
    fixtures = ['agents.json', 'devices.json', 'events_register.json',
                'users.json']
    
    def test_get_components_device_with_register_event(self):
        device = Device.objects.get(hid="XPS13-1111-2222")
        
        self.assertEqual([], list(device.components))

class ComponentsTest(TestCase):
    fixtures = ['agents.json', 'devices.json', 'events.json', 'users.json']
    
    def test_get_components_device_without_register_event(self):
        # Device has registered as component so inherits register
        device = Device.objects.get(hid="DDR3")
        self.assertEqual([], list(device.components))