from rest_framework import serializers

from .models import Device, EntryLog, Agent


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ('uuid', 'id', 'url')


class EntryLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EntryLog
        fields = ('timestamp', 'event', 'device')#, 'agent') #XXX AgentSerializer & View


class RegisterSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    agent = serializers.CharField()
    event_time = serializers.DateTimeField()
    by_user = serializers.CharField()
    
    # XXX validate data
