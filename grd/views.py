from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Agent, Device, Event
from .serializers import (
    AddSerializer, AgentSerializer, DeviceSerializer, EventSerializer,
    EventWritableSerializer, RegisterSerializer, RemoveSerializer
)


class AgentView(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = (IsAdminUser,)


class DeviceView(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    # permission_classes = (IsAdminUser,)
    
    def get_success_event_creation_response(self, request, event):
        serializer = EventSerializer(event, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)
    
    def create_event(self, serializer, type):
        serializer.is_valid(raise_exception=True)
        
        return serializer.save(
            agent=self.request.user.agent,
            device=self.get_object(),
            type=type
        )
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def add(self, request, pk=None):
        serializer = AddSerializer(data=request.data,
                                   context={'request': request})
        event = self.create_event(serializer, type=Event.ADD)
        
        return self.get_success_event_creation_response(request, event)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def remove(self, request, pk=None):
        serializer = RemoveSerializer(data=request.data,
                                      context={'request': request,
                                               'device': self.get_object()})
        event = self.create_event(serializer, type=Event.REMOVE)
        
        return self.get_success_event_creation_response(request, event)
    
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
        
        # TODO(santiago): move this logic to the serializer
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
        
        return self.get_success_event_creation_response(request, event)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def recycle(self, request, pk=None):
        serializer = EventWritableSerializer(data=request.data,
                                             context={'request': request})
        
        event = self.create_event(serializer, type=Event.RECYCLE)
        
        return self.get_success_event_creation_response(request, event)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def collect(self, request, pk=None):
        # XXX CollectSerializer: EventSerializer + extra fields on subclasses
        serializer = EventWritableSerializer(data=request.data,
                                             context={'request': request})
        event = self.create_event(serializer, type=Event.COLLECT)
        
        return self.get_success_event_creation_response(request, event)


class EventView(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
