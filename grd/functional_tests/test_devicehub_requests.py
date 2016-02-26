import unittest

from grd.functional_tests import utils
from grd.functional_tests.common import BaseTestCase
    
class RegisterTest(BaseTestCase):
    def test_0(self):
        data = utils.load_json('data/register_0.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')
        
        # TODO more extensive test validation
        new_device_url = response.data['device']
    
    def test_1(self):
        data = utils.load_json('data/register_1.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')
    
    def test_2(self):
        data = utils.load_json('data/register_2.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')
    
    def test_3(self):
        data = utils.load_json('data/register_3.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')
    
    def test_no_hid(self):
        data = utils.load_json('data/register_no_hid.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')


class AllocateTest(BaseTestCase):
    def register_and_allocate(self, number):
        # register
        data = utils.load_json('data/register_%s.json' % number)
        response = self.client.post('/api/devices/register/', data=data)
        hid = data["device"]["hid"]
        
        # allocate
        data = utils.load_json('data/allocate_%s.json' % number)
        response = self.client.post('/api/devices/%s/allocate/' % hid, data=data)
        return response
    
    def test_1(self):
        response = self.register_and_allocate(1)
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Allocate')
    
    def test_2(self):
        response = self.register_and_allocate(2)
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Allocate')
    
    def test_3(self):
        response = self.register_and_allocate(3)
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Allocate')
