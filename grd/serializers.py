from rest_framework import serializers

from .models import Device, EntryLog, Agent


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ('id', )


class EntryLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EntryLog
        fields = ('timestamp', 'event', 'device', 'agent')
