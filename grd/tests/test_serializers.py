import unittest

from django.test import TestCase

from grd.serializers import DeviceSerializer


class DeviceSerializerTest(TestCase):
    
    def test_deserializing_valid_data(self):
        data = {
            'id': '//xsr.cat/device/1234',
            'hid': 'XPS13-1111-2222',
            'type': 'computer',
        }
        serializer = DeviceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # check if deserialized object is a valid object
        obj = serializer.save()
        obj.full_clean()
    
    def test_deserializing_invalid_id(self):
        data = {
            'id': None,
            'hid': 'XPS13-1111-2222',
            'type': 'computer',
        }
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_deserializing_invalid_hid(self):
        data = {
            'id': '//xsr.cat/device/1234',
            'hid': None,
            'type': 'computer',
        }
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_deserializing_invalid_type(self):
        data = {
            'id': '//xsr.cat/device/1234',
            'hid': 'XPS13-1111-2222',
            'type': 'foo',
        }
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
