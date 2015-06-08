from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Device, Event
from .serializers import (
    AddSerializer, DeviceSerializer, EventSerializer, RecycleSerializer,
    RegisterSerializer
)


class DeviceView(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    # permission_classes = (IsAdminUser,)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def add(self, request, pk=None):
        device = self.get_object()
        serializer = AddSerializer(data=request.data,
                                   context={'request': request})
        
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        agent = request.user.agent
        
        # create event
        event = device.events.create(type=Event.ADD, agent=agent,
                                     event_time=data['event_time'],
                                     by_user=data['by_user'])
        
        for device in data['components']:
            event.components.add(device)
        
        headers = {'Location': reverse('event-detail', args=[event.pk],
                                       request=request)}
        return Response('{}', status=status.HTTP_201_CREATED, headers=headers)
    
    @detail_route(methods=['get'])
    def events(self, request, pk=None):
        device = self.get_object()
        queryset = Event.objects.related_to_device(device)
        serializer = EventSerializer(queryset, many=True,
                                     context={'request': request})
        return Response(serializer.data)
    
    @list_route(methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data,
                                        context={'request': request})
        
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # create devices and events
        try:
            dev = Device.objects.get(hid=data['device']['hid'])
        except Device.DoesNotExist:
            dev = Device.objects.create(**data['device'])
        agent = request.user.agent
        event = dev.events.create(type=Event.REGISTER, agent=agent,
                                  event_time=data['event_time'],
                                  by_user=data['by_user'])
        
        for component in data['components']:
            try:
                device = Device.objects.get(hid=component['hid'])
            except Device.DoesNotExist:
                event.components.create(**component)
            else:
                event.components.add(device)
        
        serializer = EventSerializer(event, context={'request': request})
        headers = {'Location': reverse('event-detail', args=[event.pk],
                                       request=request)}
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def recycle(self, request, pk=None):
        dev = self.get_object()
        serializer = RecycleSerializer(data=request.data,
                                       context={'request': request})
        
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # create event
        agent = request.user.agent
        event = dev.events.create(type=Event.RECYCLE, agent=agent,
                                  event_time=data['event_time'],
                                  by_user=data['by_user'])
        
        # Agent should explicity define which components are recycled
        for device in data['components']:
            event.components.add(device)
        
        headers = {'Location': reverse('event-detail', args=[event.pk],
                                       request=request)}
        return Response('{}', status=status.HTTP_201_CREATED, headers=headers)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def collect(self, request, pk=None):
        dev = self.get_object()
        # XXX CollectSerializer??: base EventSerializer + extra fields on subclasses
        serializer = RecycleSerializer(data=request.data,
                                       context={'request': request})
        
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # create event
        agent = request.user.agent
        event = dev.events.create(type=Event.COLLECT, agent=agent,
                                  event_time=data['event_time'],
                                  by_user=data['by_user'])
        
        # Agent should explicity define which components are collected
        for device in data['components']:
            event.components.add(device)
        
        headers = {'Location': reverse('event-detail', args=[event.pk],
                                       request=request)}
        return Response('{}', status=status.HTTP_201_CREATED, headers=headers)


class EventView(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
