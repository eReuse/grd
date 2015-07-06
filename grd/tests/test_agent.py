from django.test import TestCase
from grd.models import Agent


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
