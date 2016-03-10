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


class ReceiveTest(BaseTestCase):
    def register_allocate_receive(self, number):
        # register
        data = utils.load_json('data/register_%s.json' % number)
        response = self.client.post('/api/devices/register/', data=data)
        hid = data["device"]["hid"]
        
        # allocate
        data = utils.load_json('data/allocate_%s.json' % number)
        response = self.client.post('/api/devices/%s/allocate/' % hid, data=data)
        
        # receive
        data = utils.load_json('data/receive_%s.json' % number)
        response = self.client.post('/api/devices/%s/receive/' % hid, data=data)
        return response
    
    def test_1(self):
        response = self.register_allocate_receive(1)
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Receive')
    
    def test_2_receiver_not_in_allocated_users_of_device(self):
        response = self.register_allocate_receive(2)
        self.assertEqual(400, response.status_code, response.content)
    
    def test_2a_unspecified_receiver(self):
        response = self.register_allocate_receive('2a')
        self.assertEqual(400, response.status_code, response.content)
        self.assertIn("receiver", response.data)
    
    def test_3_unspecified_receiver_type(self):
        response = self.register_allocate_receive(3)
        self.assertEqual(400, response.status_code, response.content)
        self.assertIn("receiverType", response.data)
    
    def test_3a_invalid_receiver_type(self):
        response = self.register_allocate_receive('3a')
        self.assertEqual(400, response.status_code, response.content)
