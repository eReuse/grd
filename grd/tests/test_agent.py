from django.test import TestCase
from grd.models import Agent


class AgentTest(TestCase):
    fixtures = ['agents.json', 'users.json']
    
    def test_agent_representation(self):
        for agent in Agent.objects.all():
            self.assertIsNotNone(repr(agent))
