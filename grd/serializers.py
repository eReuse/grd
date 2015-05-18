from rest_framework import serializers

from .models import Device, EntryLog, Agent


class SimpleDeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ('url',)


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    components = SimpleDeviceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Device
        fields = ('uuid', 'url', 'id', 'hid', 'type', 'components')
        read_only_fields = ('uuid', 'url', 'components')


class EntryLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EntryLog
        fields = ('timestamp', 'event', 'device')#, 'agent') #XXX AgentSerializer & View


class RegisterSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    #agent = AgentSerializer()
    agent = serializers.CharField()
    components = DeviceSerializer(many=True)
    
    class Meta:
        model = EntryLog
        fields = ('device', 'agent', 'event_time', 'by_user', 'components')
    
    # XXX validate data
