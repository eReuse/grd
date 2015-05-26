import time
import unittest

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APILiveServerTestCase

from grd.models import Agent, Device, EntryLog


class Iteration1Test(StaticLiveServerTestCase, APILiveServerTestCase):
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
        self.assertEqual(200, response.status_code,
                         "Unable to log in with provided credentials.")
        
        return response.data['token']
    
    def count_listed_objects(self, url):
        response = self.client.get(url)
        return len(response.data)
    
    def get_latest_log(self, logs):
        assert len(logs) > 0
        last_log = logs[0]
        for log in logs:
            if log['timestamp'] > last_log['timestamp']:
                last_log = log
        return last_log
    
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
        
        # It checks that the device log includes register event
        response = self.client.get(dev['url'] + 'log/')
        self.assertEqual(200, response.status_code, response.content)
        logs = response.data
        self.assertGreater(len(logs), 0)
        
        # It checks that the last log is register
        last_log = self.get_latest_log(logs)
        self.assertEqual('register', last_log['event'])
        self.assertEqual(self.agent.name, last_log['agent'])
        
        # It checks that the component has inherit the log
        for component in dev['components']:
            comp_logs = self.client.get(component['url'] + 'log/').data
            self.assertGreater(len(comp_logs), 0)
    
    def test_register_already_traced_device(self):
        # XSR wants to take a snapshot of the current status of a device
        # which is already being traced by the GRD.
        self.assertEqual(0, self.count_listed_objects('/api/devices/'))
        
        # It had registered a device
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
        self.assertEqual(2, self.count_listed_objects('/api/devices/'))
        
        # It registers a alreday traced device
        response = self.client.post('/api/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        self.assertEqual(2, self.count_listed_objects('/api/devices/'))
        new_device_url = response['Location']
        
        # It verifies that the device has the proper id
        response = self.client.get(new_device_url)
        dev = response.data
        self.assertEqual(dev['id'], data['device']['id'])
        self.assertEqual(dev['hid'], data['device']['hid'])
        
        # It checks that device includes same components
        # TODO make a more detailed validation.
        # TODO retrieve device URL and compare id, hid, type
        self.assertEqual(len(dev['components']), len(data['components']))
         
        # It checks that device log includes register event
        response = self.client.get(new_device_url + 'log/')
        self.assertEqual(200, response.status_code, response.content)
        logs = response.data
        self.assertEqual(len(logs), 2)
        
        # It checks that the last log is register
        last_log = self.get_latest_log(logs)
        self.assertEqual('register', last_log['event'])
        self.assertEqual(self.agent.name, last_log['agent'])
    
    def test_register_no_data(self):
        response = self.client.post('/api/register/', data=None)
        self.assertEqual(400, response.status_code, response.content)
    
    def test_register_invalid_data(self):
        data = {
            'device': {
                'type': 'computer',
            }
        }
        response = self.client.post('/api/register/', data=data)
        self.assertEqual(400, response.status_code, response.content)
    
    # TODO def test_register_updating_components(self):
        # It checks that device includes updated components
    
    def test_recycle_device(self):
        # Bob wants to recycle a device that he has previously
        # registered.
        # Perform actions to reach pre-conditions (register device)
        # [PRE] He registers a new device
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
        device_url = response['Location']
        
        # He recycles the device
        recycle_data = {
            'event_time': '2014-04-10T22:38:20.604391Z',
            'by_user': 'some authorized recycler',
        }
        response = self.client.post(device_url + 'recycle/', data=recycle_data)
        self.assertEqual(201, response.status_code, response.content)
        # XXX new_log_url = response['Location']
        
        # He checks that the device log includes recycle event
        response = self.client.get(device_url + 'log/')
        self.assertEqual(200, response.status_code, response.content)
        logs = response.data
        self.assertEqual(len(logs), 2)
        
        # He checks he last log
        last_log = self.get_latest_log(logs)
        self.assertEqual('recycle', last_log['event'])
        self.assertEqual(self.agent.name, last_log['agent'])
        
        # He checks that the device components do NOT have a recycle event
        dev = self.client.get(device_url).data
        for component in dev['components']:
            
            comp_logs = self.client.get(component['url'] + 'log/').data
            self.assertEqual(len(comp_logs), 1)
            
            last_log = self.get_latest_log(comp_logs)
            self.assertNotEqual('recycle', last_log['event'])
    
    def test_recycle_device_with_components(self):
        # Bob wants to recycle a device that he has previously
        # registered and its components.
        # Perform actions to reach pre-conditions (register device)
        # [PRE] He registers a new device
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
        device_url = response['Location']
        
        # He recycles the device
        recycle_data = {
            'event_time': '2014-04-10T22:38:20.604391Z',
            'by_user': 'some authorized recycler',
            'components': ['DDR3'],
        }
        response = self.client.post(device_url + 'recycle/', data=recycle_data)
        self.assertEqual(201, response.status_code, response.content)
        # XXX new_log_url = response['Location']
        
        # He checks that the device log includes recycle event
        response = self.client.get(device_url + 'log/')
        self.assertEqual(200, response.status_code, response.content)
        logs = response.data
        self.assertEqual(len(logs), 2)
        
        # He checks he last log
        last_log = self.get_latest_log(logs)
        self.assertEqual('recycle', last_log['event'])
        self.assertEqual(self.agent.name, last_log['agent'])
        
        # He checks that the device components have too a recycle event
        dev = self.client.get(device_url).data
        for component in dev['components']:
            
            comp_logs = self.client.get(component['url'] + 'log/').data
            self.assertEqual(len(comp_logs), 2)
            
            last_log = self.get_latest_log(comp_logs)
            self.assertEqual('recycle', last_log['event'])
    
    def test_recycle_no_data(self):
        # [PRE] He registers a new device
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
        device_url = response['Location']
        
        # He recycles the device
        response = self.client.post(device_url + 'recycle/', data=None)
        self.assertEqual(400, response.status_code, response.content)
    
    def test_recycle_invalid_data(self):
        # [PRE] He registers a new device
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
        device_url = response['Location']
        
        # He recycles the device
        recycle_data = {
            'event_time': '2014-04-10T22:38:20.604391Z',
            'components': ['DDR3'],
        }
        response = self.client.post(device_url + 'recycle/', data=recycle_data)
        self.assertEqual(400, response.status_code, response.content)


class ApiTest(StaticLiveServerTestCase, APILiveServerTestCase):
    
    def test_retrieve_api_base(self):
        response = self.client.get('/api/')
        self.assertEqual(200, response.status_code)
    
    def test_retrieve_device_list(self):
        response = self.client.get('/api/devices/')
        self.assertEqual(200, response.status_code)
