from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APILiveServerTestCase

from grd.models import Device
from .common import BaseTestCase


class ApiTest(StaticLiveServerTestCase, APILiveServerTestCase):
    fixtures = ['agents.json', 'devices.json', 'events.json', 'users.json']
    
    def test_retrieve_api_base(self):
        response = self.client.get('/api/')
        self.assertEqual(200, response.status_code)
    
    def test_retrieve_device_list(self):
        response = self.client.get('/api/devices/')
        self.assertEqual(403, response.status_code)
    
    def test_retrieve_event_list(self):
        response = self.client.get('/api/events/')
        self.assertEqual(403, response.status_code)
    
    def test_retrieve_event_detail(self):
        response = self.client.get('/api/events/1/')
        self.assertEqual(403, response.status_code)


class ApiSuperuserTest(BaseTestCase):
    fixtures = ['agents.json', 'devices.json', 'events.json', 'users.json']
    
    def setUp(self):
        # authenticate the user
        token = self.get_user_token('ereuse', 'ereuse')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    
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
    
    def test_retrieve_device_metrics(self):
        # TODO include other metrics when are implemented
        device = Device.objects.first()
        response = self.client.get('/api/devices/%s/metrics/' % device.pk)
        self.assertEqual(200, response.status_code)
        metrics = response.data
        self.assertIn('running_time', metrics)
