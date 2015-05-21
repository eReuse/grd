from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .models import Agent, Device, EntryLog
from .serializers import DeviceSerializer, EntryLogSerializer, RegisterSerializer


class DeviceView(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    #permission_classes = (IsAdminUser,)


class DeviceLog(viewsets.ReadOnlyModelViewSet):
    queryset = EntryLog.objects.all()
    serializer_class = EntryLogSerializer
    
    def list(self, request, pk=None):
        device = get_object_or_404(Device, pk=pk)
        queryset = EntryLog.objects.related_to_device(device)
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)
        

class Register(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        if not request.data:
            return Response({'invalid_request': 'empty POST request'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        
        # create devices and logs
        try:
            dev = Device.objects.get(id=data['device']['id'])
        except Device.DoesNotExist:
            dev = Device.objects.create(**data['device'])
        agent = request.user.agent
        log = dev.logs.create(event=Device.REGISTER, agent=agent,
                        event_time=data['event_time'],
                        by_user=data['by_user'])
        
        for component in data['components']:
            try:
                device = Device.objects.get(id=component['id'])
            except Device.DoesNotExist:
                log.components.create(**component)
            else:
                log.components.add(device)
        
        headers = {'Location': reverse('device-detail', args=[dev.pk], request=request)}
        return Response('{}', status=status.HTTP_201_CREATED, headers=headers)
