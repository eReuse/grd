import json
import os
import unittest

from grd.functional_tests.common import BaseTestCase


class RegisterTest(BaseTestCase):
    def load_json(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path) as request_file:
            data = json.load(request_file)
        return data
    
    def test_0(self):
        data = self.load_json('data/register_0.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')
        
        # TODO more extensive test validation
        new_device_url = response.data['device']
    
    def test_1(self):
        data = self.load_json('data/register_1.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')
    
    def test_2(self):
        data = self.load_json('data/register_2.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')
    
    def test_3(self):
        data = self.load_json('data/register_3.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')
    
    def test_no_hid(self):
        data = self.load_json('data/register_no_hid.json')
        response = self.client.post('/api/devices/register/', data=data)
        
        self.assertEqual(201, response.status_code, response.content)
        self.assertEventType(response['Location'], 'Register')
