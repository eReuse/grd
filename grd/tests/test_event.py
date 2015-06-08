from django.test import TestCase
from grd.models import Event


class EventTest(TestCase):
    fixtures = ['agents.json', 'devices.json', 'events.json', 'users.json']
    
    def test_event_representation(self):
        for event in Event.objects.all():
            self.assertIsNotNone(repr(event))

