from rest_framework import serializers
from Elevator_app.models import Elevator,UserRequest

class ElevatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elevator
        fields = '__all__'

class UserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRequest
        fields = '__all__'
        read_only_fields = ['elevator']