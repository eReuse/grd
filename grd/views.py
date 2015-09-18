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
    permission_classes= (IsAuthenticated,)
    
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
    
    def post_event(self, request, type, serializer_class=None,
                   extra_context=None):
        serializer_class = serializer_class or EventWritableSerializer
        extra_context = extra_context or {}
        
        context = {'request': request}
        context.update(extra_context)
        
        serializer = serializer_class(data=request.data, context=context)
        event = self.create_event(serializer, type=type)
        
        return self.get_success_event_creation_response(request, event)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def add(self, request, pk=None):
        return self.post_event(request, Event.ADD, AddSerializer)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def remove(self, request, pk=None):
        return self.post_event(request, Event.REMOVE, RemoveSerializer,
                               extra_context={'device': self.get_object()})
    
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
        return self.post_event(request, Event.RECYCLE)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def migrate(self, request, pk=None):
        return self.post_event(request, Event.MIGRATE, MigrateSerializer)
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def allocate(self, request, pk=None):
        return self.post_event(request, Event.ALLOCATE, AllocateSerializer,
                               extra_context={'device': self.get_object()})
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def deallocate(self, request, pk=None):
        return self.post_event(request, Event.DEALLOCATE, DeallocateSerializer,
                               extra_context={'device': self.get_object()})
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def receive(self, request, pk=None):
        return self.post_event(request, Event.RECEIVE, ReceiveSerializer,
                               extra_context={'device': self.get_object()})
    
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated],
                  url_path='usage-proof')
    def usage_proof(self, request, pk=None):
        return self.post_event(request, Event.USAGEPROOF)


class EventView(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes= (IsAuthenticated,)
