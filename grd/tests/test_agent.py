import unittest

from django.test import TestCase
from grd.models import Agent, AgentUser


class AgentTest(TestCase):
    fixtures = ['agents.json', 'users.json']
    
    def test_agent_representation(self):
        for agent in Agent.objects.all():
            self.assertIsNotNone(repr(agent))
    
    def test_get_absolute_url(self):
        agent = Agent.objects.first()
        self.assertEqual(
            agent.get_absolute_url(),
            '/api/agents/%d/' % agent.pk
        )


class AgentUserTest(TestCase):

    def test_representation(self):
        obj = AgentUser(url="http://example.org/user/alice")
        self.assertIn(obj.url, repr(obj))
    
    @unittest.skip("Do we really want to normalize the URLs?")
    # XXX maybe trying to normalize it may cause more trouble
    # than helping us to avoid duplicate info.
    def test_cannonical_url(self):
        # Avoid different instances with equivalent URLS:
        from django.core.exceptions import ValidationError
        AgentUser.objects.create(url="http://example.org/user/alice")
        a = AgentUser(url="http://example.org/user/alice/")
        self.assertRaises(ValidationError, a.full_clean)
        # "https://example.org/user/alice"
        # "https://example.org/user/alice/"
