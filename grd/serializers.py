from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Agent, AgentUser, Device, Event, Location


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


class DeviceRegisterSerializer(serializers.ModelSerializer):
    hid = serializers.CharField(label='Hardware identifier.', max_length=128, default=None)
    url = serializers.URLField(source='sameAs')
    
    class Meta:
        model = Device
        fields = ('hid', 'url', 'type')
    
    def create(self, validated_data):
        obj, _ = Device.objects.get_or_create(
            hid=validated_data.pop('hid'),
            defaults=validated_data
        )
        return obj


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    components = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='device-detail'
    )
    
    class Meta:
        model = Device
        fields = ('url', 'hid', 'sameAs', 'type', 'components', 'owners')
        read_only_fields = ('url', 'components', 'owners')


class DeviceMetricsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ('url', 'running_time')
        read_only_fields = ('url', 'running_time')


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
    owner = serializers.SlugRelatedField(slug_field='url', read_only=True)
    to = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='agent-detail'
    )
    
    class Meta:
        model = Event
        fields = ('url', 'dhDate', 'grdDate', 'type', 'device', 'agent',
                  'components', 'to', 'location', 'owner')


class RegisterSerializer(serializers.ModelSerializer):
    device = DeviceRegisterSerializer()
    components = DeviceRegisterSerializer(many=True)
    location = LocationSerializer(required=False)
    
    class Meta:
        model = Event
        fields = ('device', 'date', 'dhDate', 'byUser', 'components', 'location')
    
    def save(self, agent=None, **kwargs):
        # create devices and events
        data = self.validated_data
        
        dev = DeviceRegisterSerializer().create(data.pop('device'))
        event = dev.events.create(type=Event.REGISTER, agent=agent,
                                  date=data.get('date', None),
                                  dhDate=data['dhDate'],
                                  byUser=data['byUser'])
        
        for device_data in data['components']:
            event.components.add(
                DeviceRegisterSerializer().create(device_data)
            )
        
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
        fields = ('date', 'dhDate', 'byUser', 'components', 'location')
    
    def create(self, validated_data):
        location_data = validated_data.pop('location', None)
        event = super(EventWritableSerializer, self).create(validated_data)
        
        if location_data is not None:
            Location.objects.create(event=event, **location_data)
        return event


class AllocateSerializer(EventWritableSerializer):
    owner = serializers.URLField()
    
    class Meta:
        model = Event
        fields = ('date', 'dhDate', 'byUser', 'owner', 'location')
    
    def validate_owner(self, value):
        device = self.context['device']
        if value in device.owners:
            raise serializers.ValidationError(
                "'%s' is already allocated to '%s'." % (device, value)
            )
        agent_user, _ = AgentUser.objects.get_or_create(url=value)
        return agent_user


class DeallocateSerializer(AllocateSerializer):
    class Meta(AllocateSerializer.Meta):
        pass
    
    def validate_owner(self, value):
        device = self.context['device']
        if value not in device.owners:
            raise serializers.ValidationError(
                "'%s' is not allocated to '%s'." % (device, value)
            )
        
        return AgentUser.objects.get(url=value)


class ReceiveSerializer(EventWritableSerializer):
    class Meta:
        model = Event
        fields = ('date', 'dhDate', 'byUser', 'location')
    
    def validate_byUser(self, value):
        device = self.context['device']
        if value not in device.owners:
            raise serializers.ValidationError(
                "'%s' is not allocated to '%s'." % (device, value)
            )
        
        return value


class MigrateSerializer(EventWritableSerializer):
    to = serializers.HyperlinkedRelatedField(
        view_name='agent-detail',
        queryset=Agent.objects.all(),
    )
    
    class Meta:
        model = Event
        fields = ('date', 'dhDate', 'byUser', 'components', 'to', 'location')
    
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
