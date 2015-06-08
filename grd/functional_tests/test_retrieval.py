from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APILiveServerTestCase


class ApiTest(StaticLiveServerTestCase, APILiveServerTestCase):
    fixtures = ['agents.json', 'devices.json', 'events.json', 'users.json']
    
    def test_retrieve_api_base(self):
        response = self.client.get('/api/')
        self.assertEqual(200, response.status_code)
    
    def test_retrieve_device_list(self):
        response = self.client.get('/api/devices/')
        self.assertEqual(200, response.status_code)
    
    def test_retrieve_event_list(self):
        response = self.client.get('/api/events/')
        self.assertEqual(200, response.status_code)
    
    def test_retrieve_event_detail(self):
        response = self.client.get('/api/events/1/')
        self.assertEqual(200, response.status_code)
        event = response.data
        self.assertIn('url', event)
