import time

from django.contrib.auth import get_user_model

from grd.functional_tests.common import BaseTestCase
from grd.models import Agent, Device, Event


User = get_user_model()


class MigrateTest(BaseTestCase):
    """https://www.wrike.com/open.htm?id=47891868"""
    
    # TODO fixture with a registered device
    def setUp(self):
        super(MigrateTest, self).setUp()
        
        # Initialize registered devices
        data = {
            'device': {
                'id': '//xsr.cat/device/1234',
                'hid': 'XPS13-1111-2222',
                'type': 'computer',
            },
            'event_time': '2012-04-10T22:38:20.604391Z',
            'by_user': 'foo',
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'monitor'}],
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        event_url = response['Location']
        self.device_url = self.client.get(event_url).data['device']
        
        # Create another agent to migrate devices to it
        user = User.objects.create_user('agent2', 'agent2@localhost', 'agent2')
        self.agent2 = Agent.objects.create(name='Agent2', user=user)
    
    def test_migrate_device(self):
        agent2 = self.client.get(self.agent2.get_absolute_url()).data
        event_data = {
            'event_time': '2015-04-10T22:38:20.604391Z',
            'by_user': 'foo',
            'to': agent2['url'],
        }
        
        response = self.client.post(self.device_url + 'migrate/',
                                    data=event_data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        self.assertEventType(new_event_url, 'migrate')
        
        # validate data
        event = self.client.get(new_event_url).data
        self.assertEqual(event['to'], event_data['to'])


class AddTest(BaseTestCase):
    """https://www.wrike.com/open.htm?id=47865363"""
    
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
        self.assertIn(device_two['url'], device_one['components'])
    
    def test_add_component_device_already_attached(self):
        # PRE: - 2 devices registered.
        #      - One of them is a component of the other
        event = self.device_one.events.create(
            type=Event.REGISTER, agent=self.agent, by_user='XSR',
            event_time='2014-03-10T22:38:20.604391Z'
        )
        event.components.add(self.device_two)
        
        device_one_url = '/api/devices/%s/' % self.device_one.pk
        
        # Add device 2 to device 1
        add_data = {
            'event_time': '2014-05-10T22:38:20.604391Z',
            'by_user': 'XSR',
            'components': [self.device_two.hid],
        }
        response = self.client.post(device_one_url + 'add/', data=add_data)
        self.assertEqual(400, response.status_code, response.content)


class CollectTest(BaseTestCase):
    """https://www.wrike.com/open.htm?id=47865028"""
    # TODO fixture with a registered device
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
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'monitor'}],
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        event_url = response['Location']
        self.device_url = self.client.get(event_url).data['device']
    
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
        
        # He checks the last event
        self.assertEventType(new_event_url, 'collect')
        
        # He checks that the device components do NOT have a collect event
        dev = self.client.get(self.device_url).data
        for component in dev['components']:
            comp_events = self.client.get(component + 'events/').data
            self.assertEqual(len(comp_events), 1)
            
            last_event = self.get_latest_event(comp_events)
            self.assertNotEqual('collect', last_event['type'])
    
    def test_collect_device_with_components(self):
        # Bob wants to recycle a device that he has previously
        # registered and its components.
        
        # He recycles the device specifying its components
        collect_data = {
            'event_time': '2014-04-10T22:38:20.604391Z',
            'by_user': 'some authorized collecter point',
            'components': ['DDR3'],
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
        
        # He checks the last event
        self.assertEventType(new_event_url, 'collect')
        
        # He checks that the device components have too a recycle event
        dev = self.client.get(self.device_url).data
        for component in dev['components']:
            comp_events = self.client.get(component + 'events/').data
            self.assertEqual(len(comp_events), 2,
                             "Component doesn't have collect event.")
            last_event = self.get_latest_event(comp_events)
            self.assertEqual('collect', last_event['type'])


class RegisterTest(BaseTestCase):
    """https://www.wrike.com/open.htm?id=47864362"""
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
                'id': '//xsr.cat/device/1234',
                'hid': 'XPS13-1111-2222',
                'type': 'computer',
            },
            'event_time': '2012-04-10T22:38:20.604391Z',
            'by_user': 'foo',
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'monitor'}],
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        
        # It checks that the last event is register
        self.assertEventType(response['Location'], 'register')
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
    
    def test_register_already_traced_device(self):
        # XSR wants to take a snapshot of the current status of a device
        # which is already being traced by the GRD.
        self.assertEqual(0, self.count_listed_objects('/api/devices/'))
        
        # PRE: It had registered a device
        data = {
            'device': {
                'id': '//xsr.cat/device/1234',
                'hid': 'XPS13-1111-2222',
                'type': 'computer',
            },
            'event_time': '2012-04-10T22:38:20.604391Z',
            'by_user': 'foo',
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'monitor'}],
        }
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(2, self.count_listed_objects('/api/devices/'))
        
        # It registers a alreday traced device
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        self.assertEqual(2, self.count_listed_objects('/api/devices/'))
        
        # It checks that the last event is register
        
        self.assertEventType(response['Location'], 'register')
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
    
    def test_register_updating_components(self):
        # PRE: It had registered a device
        data = {
            'device': {
                'id': '//xsr.cat/device/1234',
                'hid': 'XPS13-1111-2222',
                'type': 'computer',
            },
            'event_time': '2012-04-10T22:38:20.604391Z',
            'by_user': 'foo',
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'monitor'}],
        }
        self.client.post('/api/devices/register/', data=data)
        
        # It takes a snapshot of the device with different components
        data['components'] = [{'id': '2', 'hid': 'R5', 'type': 'monitor'}]
        response = self.client.post('/api/devices/register/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        
        # It checks that device includes updated components
        device_url = response.data['device']
        self.assertDeviceHasComponents(device_url, data['components'])


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
            'components': [{'id': '1', 'hid': 'DDR3', 'type': 'monitor'}],
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
        
        # He checks the last event
        self.assertEventType(new_event_url, 'recycle')
        
        # He checks that the device components do NOT have a recycle event
        dev = self.client.get(self.device_url).data
        for component in dev['components']:
            comp_events = self.client.get(component + 'events/').data
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
        new_event_url = response['Location']
        
        # He checks that the device event includes recycle event
        response = self.client.get(self.device_url + 'events/')
        self.assertEqual(200, response.status_code, response.content)
        events = response.data
        self.assertEqual(len(events), 2)
        
        # He checks the last event
        self.assertEventType(new_event_url, 'recycle')
        
        # He checks that the device components have too a recycle event
        dev = self.client.get(self.device_url).data
        for component in dev['components']:
            
            comp_events = self.client.get(component + 'events/').data
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
            'event_time': '2014-05-10T22:38:20.604391Z',
            'by_user': 'XSR',
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
            'event_time': '2014-12-12T12:38:20.604391Z',
            'by_user': 'XSR',
            'components': [self.device_two.hid],
        }
        response = self.client.post(device_one_url + 'remove/',
                                    data=remove_data)
        self.assertEqual(201, response.status_code, response.content)
        new_event_url = response['Location']
        
        # Check that last event is a removal
        self.assertEventType(new_event_url, 'remove')
        
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
            'event_time': '2014-12-12T12:38:20.604391Z',
            'by_user': 'XSR',
            'components': [self.device_two.hid],
        }
        response = self.client.post(device_one_url + 'remove/',
                                    data=remove_data)
        self.assertEqual(400, response.status_code, response.content)
