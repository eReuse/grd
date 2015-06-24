from django.test import TestCase
from django.utils import timezone
from grd.models import Agent, Device, Event


class EventTest(TestCase):
    fixtures = ['agents.json', 'devices.json', 'events.json', 'users.json']
    
    def test_event_representation(self):
        for event in Event.objects.all():
            self.assertIsNotNone(repr(event))
    
    def test_event_creation(self):
        e = Event.objects.create(
            type=Event.REGISTER,
            data={'to': '1', 'extra_info': 'blibli'},
            event_time=timezone.now(),
            by_user='John',
            agent=Agent.objects.first(),
            device=Device.objects.first(),
        )
        self.assertEqual('1', e.data['to'])
        self.assertEqual('blibli', e.data['extra_info'])
