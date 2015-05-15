import json
import unittest

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

### confine-utils ###
import sys
sys.path.append("/home/chiron/confine-utils")
from confine.client import utils


class Iteration1Test(unittest.TestCase):
    """https://www.wrike.com/open.htm?id=50126167"""
    
    def setUp(self):
        # TODO: we need user, password and server URL
        self.user = 'ereuse'
        self.password = 'ereuse'
        self.live_server_url = 'http://localhost:8888'
    
    def get_token(self, user, password):
        auth_token_url = "%s%s" % (self.live_server_url, '/api-token-auth/')
        data = {'username': user, 'password': password}
        data_out, response = utils.post_json(auth_token_url, data)
        self.assertEqual(200, response.status_code, "Unable to log in with provided credentials.")
        return data_out['token']
        
    def test_register_device(self):
        # XSR wants to use etraceability functionality of ereuse.
        
        # It gets authentication credentials
        self.superuser_token = self.get_token(self.user, self.password)
        self.super_auth = 'Token %s' % self.superuser_token
        
        # It access to the API register endpoint
#        response = self.client.get('/api/register/', **hdrs)
        register_url = '%s%s' % (self.live_server_url, '/api/register/')
        self.assertRaisesRegexp(
            utils.RestApiError, '.*405.*', utils.get_json, register_url,
            auth=self.super_auth
        )
        
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
        
        js, response = utils.post_json(register_url, data=data, auth=self.super_auth)
        self.assertEqual(201, response.status_code, response.content)
        new_device_url = response.headers['Location']
        
        # It checks that the device is listed
        devices_url = '%s%s' % (self.live_server_url, '/api/devices/')
        devices, _ = utils.get_json(devices_url, auth=self.super_auth)
        self.assertGreater(len(devices), 0)
        
        # It verifies that the device has the proper id
        dev, _ = utils.get_json(new_device_url, auth=self.super_auth)
        self.assertEqual(dev['id'], data['device']['id'])
        self.assertEqual(dev['hid'], data['device']['hid'])
        
        # It checks that device log includes register event
        device_log_url = '%s%s' % (new_device_url, 'log/')
        logs, response = utils.get_json(device_log_url, auth=self.super_auth)
        self.assertEqual(200, response.status_code, response.content)
        self.assertGreater(len(logs), 0)
        self.assertIn('register', [log['event'] for log in logs])


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
