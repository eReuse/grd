from django.shortcuts import render
from rest_framework import viewsets

from .models import Device
from .serializers import DeviceSerializer


class DeviceList(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    #permission_classes = (IsAdminUser,)
