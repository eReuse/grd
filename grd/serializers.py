from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Agent, Device, Event


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email',)


class AgentSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Agent
        fields = ('name', 'description', 'url', 'user')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        agent = Agent.objects.create(user=user, **validated_data)
        return agent


class SimpleDeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ('url',)


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    # TODO replace with HyperlinkedModelSerializer??
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
        fields = ('url', 'timestamp', 'type', 'device', 'agent')


class RegisterSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    components = DeviceSerializer(many=True)
    
    class Meta:
        model = Event
        fields = ('device', 'event_time', 'by_user', 'components')


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


class AddSerializer(serializers.ModelSerializer):
    components = serializers.SlugRelatedField(
        many=True,
        queryset=Device.objects.all(),
        slug_field='hid',
    )
    
    class Meta:
        model = Event
        fields = ('event_time', 'by_user', 'components')
    
    def validate_components(self, value):
        for device in value:
            if device.parent is not None:
                raise serializers.ValidationError(
                    "Device '%s' already has a parent." % device
                )
        return value


class RemoveSerializer(serializers.ModelSerializer):
    components = serializers.SlugRelatedField(
        many=True,
        queryset=Device.objects.all(),
        slug_field='hid',
    )
    
    class Meta:
        model = Event
        fields = ('event_time', 'by_user', 'components')
    
    def validate(self, data):
        device = self.context['device']
        
        for component in data['components']:
            if component.parent != device:
                raise serializers.ValidationError(
                    "Device '%s' is not a component of '%s'." % (component, device)
                )
        return data
