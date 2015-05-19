import json
import unittest

from django.contrib.auth import get_user_model
from rest_framework.test import APILiveServerTestCase

from grd.models import Agent


class Iteration1Test(APILiveServerTestCase):
    """https://www.wrike.com/open.htm?id=50126167"""
    def setUp(self):
        self.username = 'ereuse@localhost'
        self.password = 'ereuse'
        
        User = get_user_model()
        user = User.objects.create_user(self.username, self.password)
        
        self.agent = Agent.objects.create(name='XSR')
        self.agent.users.add(user)
        
        # authenticate the user
        token = self.get_user_token(self.username, self.password)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    
    def get_user_token(self, username, password):
        response = self.client.post(
            '/api-token-auth/',
            data={'username': username, 'password': password},
        )
        self.assertEqual(200, response.status_code, "Unable to log in with provided credentials.")
        
        return response.data['token']
    
    def test_register_device(self):
        # XSR wants to use etraceability functionality of ereuse.
        
        # It access to the API register endpoint
        response = self.client.get('/api/register/')
        self.assertEqual(405, response.status_code, response.content)
        
        # It registers a new device
        data = {
            'device': {
                'id': '//xsr.cat/device/1234',
                'hid': 'XPS13-1111-2222',
                'type': 'computer',
             },
            'event_time': '2012-04-10T22:38:20.604391Z',
            'by_user': 'foo',
            'components': [{'id': 1, 'hid': 'DDR3', 'type': 'monitor'}],
        }
        response = self.client.post('/api/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        new_device_url = response['Location']
        
        # It checks that the device is listed
        response = self.client.get('/api/devices/')
        devices = response.data
        self.assertGreater(len(devices), 0)
        
        # It verifies that the device has the proper id
        response = self.client.get(new_device_url)
        dev = response.data
        self.assertEqual(dev['id'], data['device']['id'])
        self.assertEqual(dev['hid'], data['device']['hid'])
        
        # It checks that device includes related components
        # TODO make a more detailed validation.
        self.assertEqual(len(dev['components']), len(data['components']))
        
        # It checks that device log includes register event
        response = self.client.get(dev['url'] + 'log/')
        self.assertEqual(200, response.status_code, response.content)
        logs = response.data
        self.assertGreater(len(logs), 0)
        
        # find last log
        last_log = logs[0]
        for log in logs:
            if log['timestamp'] > last_log['timestamp']:
                last_log = log
        
        self.assertEqual('register', last_log['event'])
        self.assertEqual(self.agent.name, last_log['agent'])


class ApiTest(APILiveServerTestCase):
    
    def test_retrieve_api_base(self):
        response = self.client.get('/api/')
        self.assertEqual(200, response.status_code)
    
    def test_retrieve_device_list(self):
        response = self.client.get('/api/devices/')
        self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
