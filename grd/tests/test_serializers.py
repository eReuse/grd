from django.test import TestCase

from grd.serializers import DeviceSerializer, DeviceRegisterSerializer


class DeviceSerializerTest(TestCase):
    
    def test_deserializing_valid_data(self):
        data = {
            'sameAs': 'http://example.org/device/1234/',
            'hid': 'XPS13-1111-2222',
            'type': 'Computer',
        }
        serializer = DeviceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # check if deserialized object is a valid object
        obj = serializer.save()
        obj.full_clean()
    
    def test_deserializing_invalid_sameAs(self):
        data = {
            'sameAs': None,
            'hid': 'XPS13-1111-2222',
            'type': 'Computer',
        }
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_deserializing_invalid_hid(self):
        data = {
            'sameAs': 'http://example.org/device/1234/',
            'hid': None,
            'type': 'Computer',
        }
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_deserializing_invalid_type(self):
        data = {
            'sameAs': 'http://example.org/device/1234/',
            'hid': 'XPS13-1111-2222',
            'type': 'foo',
        }
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class DeviceRegisterSerializerTest(TestCase):
    
    def test_unregistered_device(self):
        data = {
            'sameAs': 'http://example.org/device/1234/',
            'hid': 'XPS13-1111-2222',
            'type': 'Computer',
        }
        serializer = DeviceRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # check if deserialized object is a valid object
        obj = serializer.save()
        obj.full_clean()
    
    def test_registered_device(self):
        data = {
            'sameAs': 'http://example.org/device/1234/',
            'hid': 'XPS13-1111-2222',
            'type': 'Computer',
        }
        # PRE - already exists a Device with this HID
        from grd.models import Device
        Device.objects.create(**data)
        self.assertTrue(Device.objects.filter(hid=data['hid']).exists())
        
        serializer = DeviceRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
