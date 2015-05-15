from rest_framework import serializers

from .models import Device, EntryLog, Agent


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ('uuid', 'url', 'id', 'hid', 'type')
        read_only_fields = ('uuid', 'url')


class EntryLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EntryLog
        fields = ('timestamp', 'event', 'device')#, 'agent') #XXX AgentSerializer & View


class RegisterSerializer(serializers.Serializer):
    device = DeviceSerializer()
    #agent = AgentSerializer()
    agent = serializers.CharField()
    event_time = serializers.DateTimeField()
    by_user = serializers.CharField()
    
    # XXX validate data
