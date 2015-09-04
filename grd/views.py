from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Agent, Device, Event
from .serializers import (  # FIXME alphabetic order
    AddSerializer, AgentSerializer, DeviceSerializer, EventSerializer,
    EventWritableSerializer, MigrateSerializer, RegisterSerializer,
    RemoveSerializer, AllocateSerializer, DeallocateSerializer,
    ReceiveSerializer
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
        
        serializer.is_valid(raise_exception=True)
        event = serializer.save(agent=request.user.agent)
        
        return self.get_success_event_creation_response(request, event)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def recycle(self, request, pk=None):
        serializer = EventWritableSerializer(data=request.data,
                                             context={'request': request})
        
        event = self.create_event(serializer, type=Event.RECYCLE)
        
        return self.get_success_event_creation_response(request, event)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def migrate(self, request, pk=None):
        serializer = MigrateSerializer(data=request.data,
                                       context={'request': request})
        
        event = self.create_event(serializer, type=Event.MIGRATE)
        
        return self.get_success_event_creation_response(request, event)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def allocate(self, request, pk=None):
        serializer = AllocateSerializer(
            data=request.data,
            context={'request': request, 'device': self.get_object()}
        )
        
        event = self.create_event(serializer, type=Event.ALLOCATE)
        
        return self.get_success_event_creation_response(request, event)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def deallocate(self, request, pk=None):
        serializer = DeallocateSerializer(
            data=request.data,
            context={'request': request, 'device': self.get_object()}
        )
        event = self.create_event(serializer, type=Event.DEALLOCATE)
        
        return self.get_success_event_creation_response(request, event)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def receive(self, request, pk=None):
        serializer = ReceiveSerializer(
            data=request.data,
            context={'request': request, 'device': self.get_object()}
        )
        event = self.create_event(serializer, type=Event.RECEIVE)
        
        return self.get_success_event_creation_response(request, event)


class EventView(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
