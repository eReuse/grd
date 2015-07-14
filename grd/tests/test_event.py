from django.test import TestCase
from django.utils import timezone
from grd.models import Agent, Device, Event, Location


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
    
    def test_event_creation_with_location(self):
        e = Event.objects.create(
            type=Event.RECYCLE,
            event_time=timezone.now(),
            by_user='user1',
            agent=Agent.objects.first(),
            device=Device.objects.first(),
        )
        loc = Location.objects.create(
            event=e,
            lon=0.0,
            lat=0.0,
        )
        self.assertIsNotNone(e.location)
        self.assertEqual(e.location.lat, 0.0)
