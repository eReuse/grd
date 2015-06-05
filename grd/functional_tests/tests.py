import time
import unittest

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APILiveServerTestCase

from grd.models import Agent, Device, Event


class BaseTestCase(StaticLiveServerTestCase, APILiveServerTestCase):
    def setUp(self):
        self.username = 'ereuse'
        self.password = 'ereuse'
        
        User = get_user_model()
        user = User.objects.create_user(self.username,
                                        'test@localhost',
                                        self.password)
        
        self.agent = Agent.objects.create(name='XSR', user=user)
        
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
    
    def get_latest_event(self, events):
        assert len(events) > 0
        last_event = events[0]
        for event in events:
            if event['timestamp'] > last_event['timestamp']:
                last_event = event
        return last_event
    
    def assertEventType(self, event_url, type, agent_name=None):
        if agent_name is None:
            agent_name = self.agent.name
        
        response = self.client.get(event_url)
        self.assertEqual(200, response.status_code, response.content)
        
        event = response.data
        self.assertEqual(type, event['type'])
        self.assertEqual(agent_name, event['agent'])


class AddTest(BaseTestCase):
    """https://www.wrike.com/open.htm?id=47865363"""
    
    fixtures = ['devices.json']
    
    def test_add_component(self):
        # PRE: 2 devices registered without relationship
        device_one_url = '/api/devices/%s/' % Device.objects.get(hid="XPS13-1111-2222").pk
        device_two_url = '/api/devices/%s/' % Device.objects.get(hid="DDR3").pk
        
        # Check that device 1 doesn't have device 2 as component
        device_one = self.client.get(device_one_url).data
        device_two = self.client.get(device_two_url).data
        self.assertNotIn(device_two['url'], [comp['url'] for comp in device_one['components']])
        
        # Add device 2 to device 1
        add_data = {
            'event_time': '2014-05-10T22:38:20.604391Z',
            'by_user': 'XSR',
            'components': [device_two['hid']],
        }
        response = self.client.post(device_one_url + 'add/', data=add_data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # Check that device's last event is an addition
        self.assertEventType(new_event_url, 'add')
        
        # Check that device 1 has device 2 as component
        device_one = self.client.get(device_one_url).data
        self.assertIn(device_two['url'], [comp['url'] for comp in device_one['components']])


class CollectTest(BaseTestCase):
    """https://www.wrike.com/open.htm?id=47865028"""
    #TODO fixture with a registered device
    def setUp(self):
        super(CollectTest, self).setUp()
        
        # Initialize registered devices before collect tests
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
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        self.device_url = response['Location']
    
    def test_collect_device(self):
        collect_data = {
            'event_time': '2014-04-10T22:38:20.604391Z',
            'by_user': 'some authorized center',
        }
        
        response = self.client.post(self.device_url + 'collect/',
                                    data=collect_data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # He checks that the device event includes collect event
        response = self.client.get(self.device_url + 'events/')
        self.assertEqual(200, response.status_code, response.content)
        events = response.data
        self.assertEqual(len(events), 2)
        
        # He checks he last event
        # XXX TODO encapsulate check last event (type, agent)
        last_event = self.client.get(new_event_url).data
        self.assertEqual('collect', last_event['type'])
        self.assertEqual(self.agent.name, last_event['agent'])
        
        # He checks that the device components do NOT have a collect event
        dev = self.client.get(self.device_url).data
        for component in dev['components']:
            comp_events = self.client.get(component['url'] + 'events/').data
            self.assertEqual(len(comp_events), 1)
            
            last_event = self.get_latest_event(comp_events)
            self.assertNotEqual('collect', last_event['type'])


class RegisterTest(BaseTestCase):
    """https://www.wrike.com/open.htm?id=47864362"""
    
    def test_register_device(self):
        # XSR wants to use etraceability functionality of ereuse.
        
        # It access to the API register endpoint
        response = self.client.get('/api/devices/register/')
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
        response = self.client.post('/api/devices/register/', data=data)
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
        
        # It checks that the device event includes register event
        response = self.client.get(dev['url'] + 'events/')
        self.assertEqual(200, response.status_code, response.content)
        events = response.data
        self.assertGreater(len(events), 0)
        
        # It checks that the last event is register
        last_event = self.get_latest_event(events)
        self.assertEqual('register', last_event['type'])
        self.assertEqual(self.agent.name, last_event['agent'])
        
        # It checks that the component has inherit the event
        for component in dev['components']:
            comp_events = self.client.get(component['url'] + 'events/').data
            self.assertGreater(len(comp_events), 0)
    
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
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(2, self.count_listed_objects('/api/devices/'))
        
        # It registers a alreday traced device
        response = self.client.post('/api/devices/register/', data=data)
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
         
        # It checks that device event includes register event
        response = self.client.get(new_device_url + 'events/')
        self.assertEqual(200, response.status_code, response.content)
        events = response.data
        self.assertEqual(len(events), 2)
        
        # It checks that the last event is register
        last_event = self.get_latest_event(events)
        self.assertEqual('register', last_event['type'])
        self.assertEqual(self.agent.name, last_event['agent'])
    
    def test_register_no_data(self):
        response = self.client.post('/api/devices/register/', data=None)
        self.assertEqual(400, response.status_code, response.content)
    
    def test_register_invalid_data(self):
        data = {
            'device': {
                'type': 'computer',
            }
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(400, response.status_code, response.content)
    
    # TODO def test_register_updating_components(self):
        # It checks that device includes updated components


class RecycleTest(BaseTestCase):
    """https://www.wrike.com/open.htm?id=48035113"""
    
    def setUp(self):
        super(RecycleTest, self).setUp()
        
        # Initialize registered devices before recycle tests
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
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        self.device_url = response['Location']
    
    def test_recycle_device(self):
        # Bob wants to recycle a device that he has previously
        # registered.
        
        # He recycles the device
        recycle_data = {
            'event_time': '2014-04-10T22:38:20.604391Z',
            'by_user': 'some authorized recycler',
        }
        response = self.client.post(self.device_url + 'recycle/',
                                    data=recycle_data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # He checks that the device event includes recycle event
        response = self.client.get(self.device_url + 'events/')
        self.assertEqual(200, response.status_code, response.content)
        events = response.data
        self.assertEqual(len(events), 2)
        
        # He checks he last event
        last_event = self.client.get(new_event_url).data
        self.assertEqual('recycle', last_event['type'])
        self.assertEqual(self.agent.name, last_event['agent'])
        
        # He checks that the device components do NOT have a recycle event
        dev = self.client.get(self.device_url).data
        for component in dev['components']:
            comp_events = self.client.get(component['url'] + 'events/').data
            self.assertEqual(len(comp_events), 1)
            
            last_event = self.get_latest_event(comp_events)
            self.assertNotEqual('recycle', last_event['type'])
    
    def test_recycle_device_with_components(self):
        # Bob wants to recycle a device that he has previously
        # registered and its components.
        
        # He recycles the device specifying its components
        recycle_data = {
            'event_time': '2014-04-10T22:38:20.604391Z',
            'by_user': 'some authorized recycler',
            'components': ['DDR3'],
        }
        response = self.client.post(self.device_url + 'recycle/',
                                    data=recycle_data)
        self.assertEqual(201, response.status_code, response.content)
        # XXX new_event_url = response['Location']
        
        # He checks that the device event includes recycle event
        response = self.client.get(self.device_url + 'events/')
        self.assertEqual(200, response.status_code, response.content)
        events = response.data
        self.assertEqual(len(events), 2)
        
        # He checks he last event
        last_event = self.get_latest_event(events)
        self.assertEqual('recycle', last_event['type'])
        self.assertEqual(self.agent.name, last_event['agent'])
        
        # He checks that the device components have too a recycle event
        dev = self.client.get(self.device_url).data
        for component in dev['components']:
            
            comp_events = self.client.get(component['url'] + 'events/').data
            self.assertEqual(len(comp_events), 2)
            
            last_event = self.get_latest_event(comp_events)
            self.assertEqual('recycle', last_event['type'])
    
    def test_recycle_no_data(self):
        # He tries to recycle the device
        response = self.client.post(self.device_url + 'recycle/', data=None)
        self.assertEqual(400, response.status_code, response.content)
    
    def test_recycle_invalid_data(self):
        # He tries to recycle the device
        recycle_data = {
            'event_time': '2014-04-10T22:38:20.604391Z',
            'components': ['DDR3'],
        }
        response = self.client.post(self.device_url + 'recycle/',
                                    data=recycle_data)
        self.assertEqual(400, response.status_code, response.content)


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
