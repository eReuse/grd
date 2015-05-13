from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Device
from .serializers import DeviceSerializer


class DeviceView(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    #permission_classes = (IsAdminUser,)


class Register(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        if not request.data:
            return Response({'invalid_request': 'empty POST request'}, status=status.HTTP_400_BAD_REQUEST)
        
        # XXX create serializer to validate data
        Device.objects.create(id=request.data['device_id'])
        return Response(status=status.HTTP_201_CREATED)
