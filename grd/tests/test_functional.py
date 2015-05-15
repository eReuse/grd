import json
import unittest

from django.test import Client
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Iteration1Test(unittest.TestCase):
    """https://www.wrike.com/open.htm?id=50126167"""
    # XXX use DRF client to decouple from Django project?
    # http://www.django-rest-framework.org/api-guide/testing/#apiclient
    def setUp(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user('ereuse', 'test@ereuse.org', 'ereuse')
        from grd.models import Agent
        agent = Agent.objects.create(name='XSR')  # XXX
        self.client = Client()
    
    def test_register_device(self):
        # XSR wants to use etraceability functionality of ereuse.
        
        # It gets authentication credentials
        response = self.client.post('/api-token-auth/', data={'username': 'ereuse', 'password': 'ereuse'})
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
                'components': [], # XXX list of IDs
             },
            'agent': 'XSR', #XXX derivate from user who performs the action?
            'event_time': '2012-04-10T22:38:20.604391Z',
            'by_user': 'foo',
        }
        response = self.client.post('/api/register/', data=json.dumps(data), content_type='application/json', **hdrs)
        self.assertEqual(201, response.status_code, response.content)
        
        # It checks that the device is listed
        response = self.client.get('/api/devices/', **hdrs)
        devices = json.loads(response.content.decode())
        self.assertGreater(len(devices), 0)
        
        # It verifies that the device has the proper id
        response = self.client.get(devices[0]['url'], **hdrs)  # XXX follow 201 created
        dev = json.loads(response.content.decode())
        self.assertEqual(dev['id'], data['device']['id'])
        self.assertEqual(dev['hid'], data['device']['hid'])
        
        # It checks that device log includes register event
        response = self.client.get(dev['url'] + 'log/')
        self.assertEqual(200, response.status_code, response.content)
        logs = json.loads(response.content.decode())
        self.assertGreater(len(logs), 0)
        
        self.fail('Finish the test!')


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_retrieve_api_base(self):
        response = self.client.get('/api/')
        self.assertEqual(200, response.status_code)
    
    def test_retrieve_device_list(self):
        response = self.client.get('/api/devices/')
        self.assertEqual(200, response.status_code)


@unittest.skip
class NewVisitorTest(unittest.TestCase):
    
    def setUp(self):
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()
        self.browser = webdriver.Firefox()
    
    def tearDown(self):
        self.browser.quit()
        self.display.stop()
    
    def test_can_start_a_list_and_retrieve_it_later(self):
        # Edith has heard about a cool new online to-do app. She goes
        # to check out its API
        self.browser.get('http://dgr:8888/api/')
        
        # She notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)
        
        # She is invited to enter a to-do item straight away
        inputbox = self.browser.find_elementy_by_id('id_new_item')
        self.assertEqual(
                inputbox.get_attribute('placeholder'),
                'Enter a to-do item'
        )
        
        # She types "eReuse API spec" into a text box
        inputbox.send_keys('eReuse API spec')
        
        # When she hits enter, the page updates, and now the page lists
        # "1: eReuse API spec" as an item in a to-do list table
        inputbox.send_keys(Keys.ENTER)
        
        table = self.browser.find_elementy_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(
            any(row.text == '1: eReuse API spec' for row in rows)
        )
        
        self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
