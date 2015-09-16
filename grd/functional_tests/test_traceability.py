import time
import unittest

from django.contrib.auth import get_user_model

from grd.functional_tests.common import BaseTestCase
from grd.models import Agent, Device, Event


User = get_user_model()


class AllocateTest(BaseTestCase):
    def setUp(self):
        super(AllocateTest, self).setUp()
        # Register a device
        self.register_device()
        
    
    def test_allocate_device(self):
        # Bob wants to allocate a device to Alice.
        data = {
            'date': '2015-09-02T10:00:00.000000Z',
            'byUser': 'Bob',
            'owner': 'http://example.org/user/1',
        }
        response = self.client.post(self.device_url + 'allocate/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # He checks that the device event includes the new event
        response = self.client.get(self.device_url + 'events/')
        self.assertEqual(200, response.status_code, response.content)
        events = response.data
        self.assertEqual(len(events), 2)
        
        # He checks the last event
        self.assertEventType(new_event_url, 'Allocate')
        
        # validate Event's data
        event = self.client.get(new_event_url).data
        self.assertEqual(event['owner'], data['owner'])
        
        # validate Device's owner
        device = self.client.get(self.device_url).data
        self.assertIn(event['owner'], device['owners'])
        
    def test_allocate_multiple_users(self):
        # Bob wants to allocate the device to Alice.
        data = {
            'date': '2015-09-02T10:00:00.000000Z',
            'byUser': 'Bob',
            'owner': 'http://example.org/user/alice/',
        }
        response = self.client.post(self.device_url + 'allocate/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        
        # Bob also wants to allocate the device to Brian.
        data2 = {
            'date': '2015-09-02T10:10:00.000000Z',
            'byUser': 'Bob',
            'owner': 'http://example.org/user/brian/',
        }
        response = self.client.post(self.device_url + 'allocate/', data=data2)
        self.assertEqual(201, response.status_code, response.content)
        
        # Both are Device's owners
        device = self.client.get(self.device_url).data
        self.assertIn(data['owner'], device['owners'])
        self.assertIn(data2['owner'], device['owners'])
    
    def test_allocate_twice_same_user_to_device(self):
        # Bob wants to allocate a device to Alice.
        data = {
            'date': '2015-09-02T10:00:00.000000Z',
            'byUser': 'Bob',
            'owner': 'http://example.org/user/alice/',
        }
        response = self.client.post(self.device_url + 'allocate/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        
        # Bob tries to allocate again the device to Alice.
        response = self.client.post(self.device_url + 'allocate/', data=data)
        self.assertEqual(400, response.status_code, response.content)


class DeallocateTest(BaseTestCase):
    """https://wiki.ereuse.org/arch:events#deallocate"""
    
    def setUp(self):
        super(DeallocateTest, self).setUp()
        
        # Register a device
        self.register_device()
        
        # Allocate the device
        data = {
            'date': '2015-09-02T10:00:00.000000Z',
            'byUser': 'Bob',
            'owner': 'http://example.org/user/1',
        }
        response = self.client.post(self.device_url + 'allocate/', data=data)
        self.assertEqual(201, response.status_code, response.content)
    
    def test_deallocate_device(self):
        # Bob wants to deallocate the device from Alice.
        data = {
            'date': '2015-09-02T10:00:00.000000Z',
            'byUser': 'Bob',
            'owner': 'http://example.org/user/1',
        }
        response = self.client.post(self.device_url + 'deallocate/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # He checks the last event
        self.assertEventType(new_event_url, 'Deallocate')
        
        # validate Event's data
        event = self.client.get(new_event_url).data
        self.assertEqual(event['owner'], data['owner'])
        
        # validate Device's owner
        device = self.client.get(self.device_url).data
        self.assertNotIn(event['owner'], device['owners'])
    
    def test_deallocate_unallocated_user_of_device(self):
        # Bob wants to deallocate the device from an unallocated user.
        data = {
            'date': '2015-09-02T10:00:00.000000Z',
            'byUser': 'Bob',
            'owner': 'http://example.org/user/999/',
        }
        response = self.client.post(self.device_url + 'deallocate/', data=data)
        self.assertEqual(400, response.status_code, response.content)


class ReceiveTest(BaseTestCase):
    def setUp(self):
        super(ReceiveTest, self).setUp()
        # Register a device
        self.register_device()
    
    def test_receive_device(self):
        # Bob allocates the device to Alice.
        data = {
            'date': '2015-09-02T10:00:00.000000Z',
            'byUser': 'Bob',
            'owner': 'http://example.org/user/alice/',
        }
        response = self.client.post(self.device_url + 'allocate/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        
        # Alice receives the device
        data = {
            'date': '2015-09-04T10:50:00.000000Z',
            'byUser': 'http://example.org/user/alice/',
        }
        response = self.client.post(self.device_url + 'receive/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # Check the last event
        self.assertEventType(new_event_url, 'Receive')
    
    def test_receive_device_not_allocated(self):
        data = {
            'date': '2015-09-04T10:50:00.000000Z',
            'byUser': 'http://example.org/user/alice/',
        }
        
        # Check that Alice doesn't own the device
        device = self.client.get(self.device_url).data
        self.assertNotIn(data['byUser'], device['owners'])
        
        # Alice tries to receive a device that hasn't been allocated to her
        response = self.client.post(self.device_url + 'receive/', data=data)
        self.assertEqual(400, response.status_code, response.content)


class MigrateTest(BaseTestCase):
    """https://wiki.ereuse.org/arch:events#migrate"""
    
    def setUp(self):
        super(MigrateTest, self).setUp()
        # Register a device
        self.register_device()
        
        # Create another agent to migrate devices to it
        user = User.objects.create_user('agent2', 'agent2@localhost', 'agent2')
        self.agent2 = Agent.objects.create(name='Agent2', user=user)
    
    def test_migrate_device(self):
        agent2 = self.client.get(self.agent2.get_absolute_url()).data
        event_data = {
            'date': '2015-04-10T22:38:20.604391Z',
            'byUser': 'foo',
            'to': agent2['url'],
        }
        
        response = self.client.post(self.device_url + 'migrate/',
                                    data=event_data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        self.assertEventType(new_event_url, 'Migrate')
        
        # validate data
        event = self.client.get(new_event_url).data
        self.assertEqual(event['to'], event_data['to'])


class AddTest(BaseTestCase):
    """https://wiki.ereuse.org/arch:events#add"""
    
    fixtures = ['devices.json']
    
    def setUp(self):
        super(AddTest, self).setUp()
        self.device_one = Device.objects.get(hid="XPS13-1111-2222")
        self.device_two = Device.objects.get(hid="DDR3")
    
    def test_add_component(self):
        # PRE: 2 devices registered without relationship
        device_one_url = '/api/devices/%s/' % self.device_one.pk
        device_two_url = '/api/devices/%s/' % self.device_two.pk
        
        # Check that device 1 doesn't have device 2 as component
        device_one = self.client.get(device_one_url).data
        device_two = self.client.get(device_two_url).data
        self.assertNotIn(
            device_two['url'],
            [comp['url'] for comp in device_one['components']]
        )
        
        # Add device 2 to device 1
        add_data = {
            'date': '2014-05-10T22:38:20.604391Z',
            'byUser': 'XSR',
            'components': [device_two['hid']],
        }
        response = self.client.post(device_one_url + 'add/', data=add_data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # Check that device's last event is an addition
        self.assertEventType(new_event_url, 'Add')
        
        # Check that device 1 has device 2 as component
        device_one = self.client.get(device_one_url).data
        self.assertIn(device_two['url'], device_one['components'])
    
    def test_add_component_device_already_attached(self):
        # PRE: - 2 devices registered.
        #      - One of them is a component of the other
        event = self.device_one.events.create(
            type=Event.REGISTER, agent=self.agent, byUser='XSR',
            date='2014-03-10T22:38:20.604391Z'
        )
        event.components.add(self.device_two)
        
        device_one_url = '/api/devices/%s/' % self.device_one.pk
        
        # Add device 2 to device 1
        add_data = {
            'date': '2014-05-10T22:38:20.604391Z',
            'byUser': 'XSR',
            'components': [self.device_two.hid],
        }
        response = self.client.post(device_one_url + 'add/', data=add_data)
        self.assertEqual(400, response.status_code, response.content)


class RegisterTest(BaseTestCase):
    """https://wiki.ereuse.org/arch:events#register"""
    def assertDeviceHasComponents(self, device_url, components):
        response = self.client.get(device_url)
        self.assertNotEqual(404, response.status_code, response.content)
        device = response.data
        
        self.assertEqual(len(device['components']), len(components))
        
        device_components = []
        for dev_url in device['components']:
            dev = self.client.get(dev_url).data
            device_components.append({
                'hid': dev['hid'],
                'id': dev['id'],
                'type': dev['type'],
            })
        
        device_components = sorted(device_components, key=lambda k: k['hid'])
        components = sorted(components, key=lambda k: k['hid'])
        
        self.assertEqual(device_components, components)
    
    def test_register_device(self):
        # XSR wants to use etraceability functionality of ereuse.
        
        # It access to the API register endpoint
        response = self.client.get('/api/devices/register/')
        self.assertEqual(405, response.status_code, response.content)
        
        # It registers a new device
        data = {
            'device': {
                'id': 'http://example.org/device/1234/',
                'hid': 'XPS13-1111-2222',
                'type': 'Computer',
            },
            'date': '2012-04-10T22:38:20.604391Z',
            'byUser': 'foo',
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'Monitor'}],
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        
        # It checks that the last event is register
        self.assertEventType(response['Location'], 'Register')
        new_device_url = response.data['device']
        
        # It checks that the device is listed
        response = self.client.get('/api/devices/')
        devices = response.data
        self.assertGreater(len(devices), 0)
        
        # It verifies that the device has the proper id
        device = self.client.get(new_device_url).data
        self.assertEqual(device['id'], data['device']['id'])
        self.assertEqual(device['hid'], data['device']['hid'])
        
        # It checks that device includes related components
        self.assertDeviceHasComponents(new_device_url, data['components'])
        
        # It checks that the device event includes register event
        response = self.client.get(device['url'] + 'events/')
        self.assertEqual(200, response.status_code, response.content)
        events = response.data
        self.assertGreater(len(events), 0)
        
        # It checks that the component has inherit the event
        for component in device['components']:
            comp_events = self.client.get(component + 'events/').data
            self.assertGreater(len(comp_events), 0)
    
    def test_register_device_with_location(self):
        # PRE: It had registered a device
        data = {
            'device': {
                'id': 'http://example.org/device/1234/',
                'hid': 'XPS13-1111-2222',
                'type': 'Computer',
            },
            'components': [],
            'date': '2012-04-10T22:38:20.604391Z',
            'byUser': 'foo',
            'location': {
                'lat': 27.9878943,
                'lon': 86.9247837,
            }
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        
        # it checks that it has the proper location
        event = response.data
        self.assertIsNotNone(event['location'])
        self.assertEqual(event['location'], data['location'])
    
    def test_register_no_data(self):
        response = self.client.post('/api/devices/register/', data=None)
        self.assertEqual(400, response.status_code, response.content)
    
    def test_register_invalid_data(self):
        data = {
            'device': {
                'type': 'Computer',
            }
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(400, response.status_code, response.content)
    
    def test_register_already_traced_device(self):
        # XSR wants to take a snapshot of the current status of a device
        # which is already being traced by the GRD.
        self.assertEqual(0, self.count_listed_objects('/api/devices/'))
        
        # PRE: It had registered a device
        data = {
            'device': {
                'id': 'http://example.org/device/1234/',
                'hid': 'XPS13-1111-2222',
                'type': 'Computer',
            },
            'date': '2012-04-10T22:38:20.604391Z',
            'byUser': 'foo',
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'Monitor'}],
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(2, self.count_listed_objects('/api/devices/'))
        
        # It registers a already traced device
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        self.assertEqual(2, self.count_listed_objects('/api/devices/'))
        
        # It checks that the last event is register
        
        self.assertEventType(response['Location'], 'Register')
        new_device_url = response.data['device']
        
        # It verifies that the device has the proper id
        device = self.client.get(new_device_url).data
        self.assertEqual(device['id'], data['device']['id'])
        self.assertEqual(device['hid'], data['device']['hid'])
        
        # It checks that device includes same components
        self.assertDeviceHasComponents(device['url'], data['components'])
         
        # It checks that device event includes register event
        response = self.client.get(new_device_url + 'events/')
        self.assertEqual(200, response.status_code, response.content)
        events = response.data
        self.assertEqual(len(events), 2)
    
    def test_snapshot_updating_components(self):
        # TODO should a snapshot be replaced with add/remove events?
        # PRE: It had registered a device
        data = {
            'device': {
                'id': 'http://example.org/device/1234/',
                'hid': 'XPS13-1111-2222',
                'type': 'Computer',
            },
            'date': '2012-04-10T22:38:20.604391Z',
            'byUser': 'foo',
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'Monitor'}],
        }
        self.client.post('/api/devices/register/', data=data)
        
        # It takes a snapshot of the device with different components
        data['components'] = [{'id': '2', 'hid': 'R5', 'type': 'Monitor'}]
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        
        # It checks that device includes updated components
        device_url = response.data['device']
        self.assertDeviceHasComponents(device_url, data['components'])


class RecycleTest(BaseTestCase):
    """https://wiki.ereuse.org/arch:events#recycle"""
    
    def setUp(self):
        super(RecycleTest, self).setUp()
        
        # Initialize registered devices before recycle tests
        data = {
            'device': {
                'id': 'http://example.org/device/1234/',
                'hid': 'XPS13-1111-2222',
                'type': 'Computer',
            },
            'date': '2012-04-10T22:38:20.604391Z',
            'byUser': 'foo',
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'Monitor'}],
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        event_url = response['Location']
        self.device_url = self.client.get(event_url).data['device']
    
    def test_recycle_device(self):
        # Bob wants to recycle a device that he has previously
        # registered.
        
        # He recycles the device
        recycle_data = {
            'date': '2014-04-10T22:38:20.604391Z',
            'byUser': 'some authorized recycler',
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
        
        # He checks the last event
        self.assertEventType(new_event_url, 'Recycle')
        
        # He checks that the device components do NOT have a recycle event
        dev = self.client.get(self.device_url).data
        for component in dev['components']:
            comp_events = self.client.get(component + 'events/').data
            self.assertEqual(len(comp_events), 1)
            
            last_event = self.get_latest_event(comp_events)
            self.assertNotEqual('Recycle', last_event['type'])
    
    def test_recycle_device_with_components(self):
        # Bob wants to recycle a device that he has previously
        # registered and its components.
        
        # He recycles the device specifying its components
        recycle_data = {
            'date': '2014-04-10T22:38:20.604391Z',
            'byUser': 'some authorized recycler',
            'components': ['DDR3'],
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
        
        # He checks the last event
        self.assertEventType(new_event_url, 'Recycle')
        
        # He checks that the device components have too a recycle event
        dev = self.client.get(self.device_url).data
        for component in dev['components']:
            
            comp_events = self.client.get(component + 'events/').data
            self.assertEqual(len(comp_events), 2)
            
            last_event = self.get_latest_event(comp_events)
            self.assertEqual('Recycle', last_event['type'])
    
    def test_recycle_device_with_location(self):
        data = {
            'date': '2014-04-10T22:38:20.604391Z',
            'byUser': 'some authorized recycler',
            'location': {
                'lat': 27.9878943,
                'lon': 86.9247837,
            }
        }
        response = self.client.post(self.device_url + 'recycle/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        
        # it checks that it has the proper location
        event = response.data
        self.assertIsNotNone(event['location'])
        self.assertEqual(event['location'], data['location'])
    
    def test_recycle_no_data(self):
        # He tries to recycle the device
        response = self.client.post(self.device_url + 'recycle/', data=None)
        self.assertEqual(400, response.status_code, response.content)
    
    def test_recycle_invalid_data(self):
        # He tries to recycle the device
        recycle_data = {
            'date': '2014-04-10T22:38:20.604391Z',
            'components': ['DDR3'],
        }
        response = self.client.post(self.device_url + 'recycle/',
                                    data=recycle_data)
        self.assertEqual(400, response.status_code, response.content)


class RemoveTest(BaseTestCase):
    fixtures = ['devices.json']
    
    def setUp(self):
        super(RemoveTest, self).setUp()
        self.device_one = Device.objects.get(hid="XPS13-1111-2222")
        self.device_two = Device.objects.get(hid="DDR3")
    
    def test_remove_component(self):
        # PRE: 2 registered devices that are related
        device_one_url = '/api/devices/%s/' % self.device_one.pk
        device_two_url = '/api/devices/%s/' % self.device_two.pk
        
        add_data = {
            'date': '2014-05-10T22:38:20.604391Z',
            'byUser': 'XSR',
            'components': [self.device_two.hid],
        }
        response = self.client.post(device_one_url + 'add/', data=add_data)
        self.assertEqual(201, response.status_code, response.content)
        
        # Check that device 1 has device 2 as component
        device_one = self.client.get(device_one_url).data
        device_two = self.client.get(device_two_url).data
        self.assertIn(device_two['url'], device_one['components'])
        
        # Remove device 2 of device 1
        remove_data = {
            'date': '2014-12-12T12:38:20.604391Z',
            'byUser': 'XSR',
            'components': [self.device_two.hid],
        }
        response = self.client.post(device_one_url + 'remove/',
                                    data=remove_data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # Check that last event is a removal
        self.assertEventType(new_event_url, 'Remove')
        
        # Check that device 1 doesn't have device 2 as component anymore
        device_one = self.client.get(device_one_url).data
        device_two = self.client.get(device_two_url).data
        self.assertNotIn(device_two['url'], device_one['components'])
    
    def test_remove_component_not_in_the_device(self):
        # PRE: 2 registered devices that are NOT related
        # Check that device 1 doesn't have device 2 as component
        device_one_url = '/api/devices/%s/' % self.device_one.pk
        device_two_url = '/api/devices/%s/' % self.device_two.pk
        
        device_one = self.client.get(device_one_url).data
        device_two = self.client.get(device_two_url).data
        self.assertNotIn(device_two['url'], device_one['components'])
        
        # Remove device 2 of device 1
        remove_data = {
            'date': '2014-12-12T12:38:20.604391Z',
            'byUser': 'XSR',
            'components': [self.device_two.hid],
        }
        response = self.client.post(device_one_url + 'remove/',
                                    data=remove_data)
        self.assertEqual(400, response.status_code, response.content)


class UsageProofTest(BaseTestCase):
    
    def setUp(self):
        super(UsageProofTest, self).setUp()
        self.register_device()
    
    def test_report_device_usage(self):
        # Alice sends an usageproof event of the device
        data = {
            'date': '2015-09-16T12:43:00.000000Z',
            'byUser': 'http://example.org/user/alice/',
        }
        response = self.client.post(self.device_url + 'usage-proof/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # Check the last event
        self.assertEventType(new_event_url, 'UsageProof')
