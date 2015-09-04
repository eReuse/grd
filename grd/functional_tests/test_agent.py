from django.contrib.auth import get_user_model

from grd.functional_tests.common import BaseTestCase


class AgentTest(BaseTestCase):
    
    def setUp(self):
        # Override base test case because we don't want any default
        # agent nor user but a superuser (administrator).
        self.username = 'admin'
        self.password = 'adminpass'
        User = get_user_model()
        User.objects.create_superuser(
            self.username,
            'test@localhost',
            self.password
        )
        
        # log in as superuser
        token = self.get_user_token(self.username, self.password)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    
    def test_CRUD(self):
        # create
        data = {
            'name': 'Xarxa Support Reutilització',
            'description': 'Reutilitza.cat és una xarxa social.',
            'user': {
                'username': 'xsr',
                'email': 'xsr@localhost',
            },
            # Don't set password, user should request to generate it.
        }
        response = self.client.post('/api/agents/', data=data)
        self.assertEqual(201, response.status_code, response.content)
        new_agent_url = response['Location']
        
        # read
        response = self.client.get(new_agent_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(data['name'], response.data['name'])
        
        # update
        new_data = {'name': 'XSR'}
        response = self.client.patch(new_agent_url, data=new_data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(new_data['name'], response.data['name'])
        
        # list
        response = self.client.get('/api/agents/')
        self.assertEqual(200, response.status_code)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(response.data[0]['url'], new_agent_url)
        
        # delete
        response = self.client.delete(new_agent_url)
        self.assertEqual(204, response.status_code)
        response = self.client.get('/api/agents/')
        self.assertEqual(0, len(response.data))
