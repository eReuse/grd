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
    #XXX AgentSerializer & View
    agent = serializers.SlugRelatedField(read_only=True, slug_field='name')
    
    class Meta:
        model = EntryLog
        fields = ('timestamp', 'event', 'device', 'agent')


class RegisterSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    components = DeviceSerializer(many=True)
    
    class Meta:
        model = EntryLog
        fields = ('device', 'event_time', 'by_user', 'components')
    
    # XXX validate data


class RecycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryLog
        fields = ('event_time', 'by_user')
