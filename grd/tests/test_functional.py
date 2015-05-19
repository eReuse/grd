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
        
        agent = Agent.objects.create(name='XSR')
        agent.users.add(user)
    
    def test_register_device(self):
        # XSR wants to use etraceability functionality of ereuse.
        
        # It gets authentication credentials
        response = self.client.post(
            '/api-token-auth/',
            data={'username': self.username, 'password': self.password}
        )
        self.assertEqual(200, response.status_code, "Unable to log in with provided credentials.")
        
        json_res = json.loads(response.content.decode())
        hdrs = {
            'HTTP_AUTHORIZATION': "Token %s" % json_res['token'],
            #'accept': 'application/json',
            #'content-type'] = 'application/json',
        }
        
        # It access to the API register endpoint
        response = self.client.get('/api/register/', **hdrs)
        self.assertEqual(405, response.status_code, response.content)
        
        # It registers a new device
        data = {
            'device': {
                'id': '//xsr.cat/device/1234',
                'hid': 'XPS13-1111-2222',
                'type': 'computer',
             },
            'agent': 'XSR', #XXX derivate from user who performs the action?
            'event_time': '2012-04-10T22:38:20.604391Z',
            'by_user': 'foo',
            'components': [{'id': 1, 'hid': 'DDR3', 'type': 'monitor'}],
        }
        response = self.client.post('/api/register/', data=json.dumps(data), content_type='application/json', **hdrs)
        self.assertEqual(201, response.status_code, response.content)
        new_device_url = response['Location']
        
        # It checks that the device is listed
        response = self.client.get('/api/devices/', **hdrs)
        devices = json.loads(response.content.decode())
        self.assertGreater(len(devices), 0)
        
        # It verifies that the device has the proper id
        response = self.client.get(new_device_url, **hdrs)
        dev = json.loads(response.content.decode())
        self.assertEqual(dev['id'], data['device']['id'])
        self.assertEqual(dev['hid'], data['device']['hid'])
        
        # It checks that device includes related components
        # TODO make a more detailed validation.
        self.assertEqual(len(dev['components']), len(data['components']))
        
        # It checks that device log includes register event
        response = self.client.get(dev['url'] + 'log/')
        self.assertEqual(200, response.status_code, response.content)
        logs = json.loads(response.content.decode())
        self.assertGreater(len(logs), 0)
        self.assertIn('register', [log['event'] for log in logs])


class ApiTest(APILiveServerTestCase):
    
    def test_retrieve_api_base(self):
        response = self.client.get('/api/')
        self.assertEqual(200, response.status_code)
    
    def test_retrieve_device_list(self):
        response = self.client.get('/api/devices/')
        self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
