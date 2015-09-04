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
            date=timezone.now(),
            byUser='John',
            agent=Agent.objects.first(),
            device=Device.objects.first(),
        )
        self.assertEqual('1', e.data['to'])
        self.assertEqual('blibli', e.data['extra_info'])
    
    def test_event_creation_with_location(self):
        e = Event.objects.create(
            type=Event.RECYCLE,
            date=timezone.now(),
            byUser='user1',
            agent=Agent.objects.first(),
            device=Device.objects.first(),
        )
        Location.objects.create(
            event=e,
            lon=0.0,
            lat=0.0,
        )
        self.assertIsNotNone(e.location)
        self.assertEqual(e.location.lat, 0.0)


    def test_event_to(self):
        e = Event.objects.create(
            type=Event.REGISTER,
            date=timezone.now(),
            byUser='John',
            agent=Agent.objects.first(),
            device=Device.objects.first(),
        )
        self.assertEqual(None, e.to)
        
        migrate_to = str(Agent.objects.last().pk)
        e = Event.objects.create(
            type=Event.MIGRATE,
            data={'to': migrate_to},
            date=timezone.now(),
            byUser='John',
            agent=Agent.objects.first(),
            device=Device.objects.first(),
        )
        self.assertEqual(migrate_to, e.to)
