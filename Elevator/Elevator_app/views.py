from django.shortcuts import render
from rest_framework.decorators import action
from Elevator_app.models import Elevator, UserRequest
from Elevator_app.serializers import ElevatorSerializer, UserRequestSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response

# Create your views here.
class ElevatorViewSet(viewsets.ModelViewSet):
    queryset = Elevator.objects.all()
    serializer_class = ElevatorSerializer

    @action(detail=False, methods=['post'])
    def initialize_system(self, request):
        num_elevators = request.data.get('num_elevators')

        if not isinstance(num_elevators, int) or num_elevators <= 0:
            return Response({"error": "Please provide a valid number of elevators to initialize the system"}, status=status.HTTP_400_BAD_REQUEST)

        Elevator.objects.all().delete()

        elevators = [Elevator.objects.create() for _ in range(num_elevators)]
        elevator_data = [{'elevator_id': elevator.pk} for elevator in elevators]

        return Response({"message": f"{num_elevators} elevators initialized successfully.", "elevators": elevator_data}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def save_request(self, request):
        """
        API to save a user request and assign the most optimal elevator to the request
        """
        requested_from_floor = request.data.get('requested_floor')
        requested_to_floor = request.data.get('destination_floor')
        print(requested_from_floor)
        print(requested_to_floor)

        if not requested_from_floor or not requested_to_floor or not isinstance(requested_from_floor, int) or not isinstance(requested_to_floor, int) or requested_from_floor <= 0 or requested_to_floor <= 0:
            return Response({'error': 'Invalid floor number provided.'}, status=status.HTTP_400_BAD_REQUEST)

        elevators = Elevator.objects.filter(in_maintenance=False,is_door_open=False)

        if not elevators:
            return Response({'error': 'No elevators available.'}, status=status.HTTP_400_BAD_REQUEST)

        distances = []
        for elevator in elevators:
            non_completed = UserRequest.objects.filter(elevator=elevator,is_complete=False).order_by('created_at').first()
            if non_completed:
                distance = abs(requested_from_floor - non_completed.requested_to_floor)
            else:
                distance = abs(requested_from_floor - elevator.current_floor)
            distances.append({'elevator': elevator, 'distance': distance})

        sorted_elevators = sorted(distances, key=lambda x: x['distance'])

        elevator = sorted_elevators[0]['elevator']

        UserRequest.objects.create(elevator=elevator, current_floor=elevator.current_floor,requested_floor=requested_from_floor,destination_floor=requested_to_floor)

        return Response({'message': 'User request saved successfully.',
                        'elevator_id': elevator.pk,},
                        status=status.HTTP_201_CREATED)

 