from rest_framework import serializers

from .models import Device, Event


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


class EventSerializer(serializers.HyperlinkedModelSerializer):
    # XXX AgentSerializer & View
    agent = serializers.SlugRelatedField(read_only=True, slug_field='name')
    
    class Meta:
        model = Event
        fields = ('timestamp', 'event', 'device', 'agent')


class RegisterSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    components = DeviceSerializer(many=True)
    
    class Meta:
        model = Event
        fields = ('device', 'event_time', 'by_user', 'components')
    
    # XXX validate data


class RecycleSerializer(serializers.ModelSerializer):
    components = serializers.SlugRelatedField(
        many=True,
        default=[],
        queryset=Device.objects.all(),
        slug_field='hid',
    )
    
    class Meta:
        model = Event
        fields = ('event_time', 'by_user', 'components')
