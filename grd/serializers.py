from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Agent, Device, Event, Location


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


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    components = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='device-detail'
    )
    
    class Meta:
        model = Device
        fields = ('url', 'hid', 'id', 'type', 'components')
        read_only_fields = ('url', 'components')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('lat', 'lon')


class EventSerializer(serializers.HyperlinkedModelSerializer):
    agent = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='agent-detail'
    )
    location = LocationSerializer()
    to = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='agent-detail'
    )
    
    class Meta:
        model = Event
        fields = ('url', 'timestamp', 'type', 'device', 'agent', 'components',
                  'to', 'location')


class RegisterSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    components = DeviceSerializer(many=True)
    location = LocationSerializer(required=False)
    
    class Meta:
        model = Event
        fields = ('device', 'event_time', 'by_user', 'components', 'location')
    
    def save(self, agent=None, **kwargs):
        # create devices and events
        data = self.validated_data
        
        try:
            dev = Device.objects.get(hid=data['device']['hid'])
        except Device.DoesNotExist:
            dev = Device.objects.create(**data['device'])
        event = dev.events.create(type=Event.REGISTER, agent=agent,
                                  event_time=data['event_time'],
                                  by_user=data['by_user'])
        
        for component in data['components']:
            try:
                device = Device.objects.get(hid=component['hid'])
            except Device.DoesNotExist:
                event.components.create(**component)
            else:
                event.components.add(device)
        
        # TODO refactor location creation
        location = LocationSerializer(data=data.get('location', None))
        if location.is_valid():
            location.validated_data['event_id'] = event.pk
            location.create(location.validated_data)
        
        return event


class EventWritableSerializer(serializers.ModelSerializer):
    components = serializers.SlugRelatedField(
        many=True,
        default=[],
        queryset=Device.objects.all(),
        slug_field='hid',
    )
    location = LocationSerializer(required=False)
    
    class Meta:
        model = Event
        fields = ('event_time', 'by_user', 'components', 'location')
    
    def create(self, validated_data):
        location_data = validated_data.pop('location', None)
        event = super(EventWritableSerializer, self).create(validated_data)
        
        if location_data is not None:
            Location.objects.create(event=event, **location_data)
        return event


class MigrateSerializer(EventWritableSerializer):
    to = serializers.HyperlinkedRelatedField(
        view_name='agent-detail',
        queryset=Agent.objects.all(),
    )
    
    class Meta:
        model = Event
        fields = ('event_time', 'by_user', 'components', 'to', 'location')
    
    def save(self, **kwargs):
        to = self.validated_data.pop('to')
        # convert all HStore data to string
        self.validated_data['data'] = {'to': str(to.pk)}
        
        return super(MigrateSerializer, self).save(**kwargs)


class AddSerializer(EventWritableSerializer):
    class Meta(EventWritableSerializer.Meta):
        pass
    
    def validate_components(self, value):
        for device in value:
            if device.parent is not None:
                raise serializers.ValidationError(
                    "Device '%s' already has a parent." % device
                )
        return value


class RemoveSerializer(EventWritableSerializer):
    class Meta(EventWritableSerializer.Meta):
        pass
    
    def validate(self, data):
        device = self.context['device']
        
        for component in data['components']:
            if component.parent != device:
                raise serializers.ValidationError(
                    "Device '%s' is not a component of '%s'." % (component, device)
                )
        return data
