import redis
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from Elevator_app.serializers import ElevatorSerializer, UserRequestSerializer
from Elevator_app.models import Elevator, UserRequest
from operator import itemgetter
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

"https://docs.google.com/document/d/1ZlJKfawiwqaEy2qoa0iAOB36Y0Ph5K2_zsvLcVJJBxk/edit"
class ElevatorViewSet(viewsets.ModelViewSet):
    queryset = Elevator.objects.all()
    serializer_class = ElevatorSerializer

    @action(detail=False, methods=["post"])
    def initialize_elevators(self, request):
        """
        Initializes the elevator system with the specified number of elevators.
        Params: request - HTTP request with 'number_of_elevators' in data.
        Returns: JsonResponse - Success message and elevator data with IDs.
        Example: POST /initialize_elevators/ {"number_of_elevators": 3}
        Response: {"message": "3 elevators initialized successfully", "elevators": [{"elevator_id": 1}, {"elevator_id": 2}, {"elevator_id": 3}]}
        """
        num_elevators = request.data.get("number_of_elevators")
        if not isinstance(num_elevators, int) or num_elevators <= 0:
            return Response(
                {
                    "error": "Please provide a valid number of elevators to initialize the system"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        Elevator.objects.all().delete()
        elevators = [Elevator.objects.create() for _ in range(num_elevators)]
        elevator_data = [{"elevator_id": elevator.pk} for elevator in elevators]

        return JsonResponse(
            {
                "message": f"{num_elevators} elevators initialized successfully.",
                "elevators": elevator_data,
            },
            status=status.HTTP_200_OK,
        )


    @action(detail=False, methods=["post"])
    def save_user_request(self, request):
        """
        API to save a user request and assign the most optimal elevator.
        Parameters:
            - request: HTTP request with 'requested_floor' and 'destination_floor' in data.
        Returns:
            - JsonResponse: Success message and assigned elevator ID.
        Example:
            >>> POST /save_user_request/ {"requested_floor": 2, "destination_floor": 6}
            >>> Response: {"message": "User request saved successfully.", "elevator_id": 1}

        """
        requested_from_floor = request.data.get("requested_floor")
        requested_to_floor = request.data.get("destination_floor")
        if (
            not requested_from_floor
            or not requested_to_floor
            or not isinstance(requested_from_floor, int)
            or not isinstance(requested_to_floor, int)
            or requested_from_floor <= 0
            or requested_to_floor <= 0
        ):
            return JsonResponse(
                {"error": "Invalid floor number provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elevators = Elevator.objects.filter(in_maintenance=False, is_door_open=False)
        if not elevators:
            return JsonResponse(
                {"error": "No elevators available."}, status=status.HTTP_400_BAD_REQUEST
            )
        distances = []
        for elevator in elevators:
            non_completed = (
                UserRequest.objects.filter(elevator=elevator, is_complete=False)
                .order_by("created_at")
                .first()
            )
            if non_completed:
                distance = abs(requested_from_floor - non_completed.destination_floor)
            else:
                distance = abs(requested_from_floor - elevator.current_floor)
            distances.append({"elevator": elevator, "distance": distance})

        sorted_elevators = sorted(distances, key=itemgetter("distance"))
        elevator = sorted_elevators[0]["elevator"]
        UserRequest.objects.create(
            elevator=elevator,
            current_floor=elevator.current_floor,
            requested_floor=requested_from_floor,
            destination_floor=requested_to_floor,
        )
        return JsonResponse(
            {"message": "User request saved successfully.", "elevator_id": elevator.pk},
            status=status.HTTP_201_CREATED,
        )


    @action(detail=True, methods=["get"])
    def get_user_requests(self, request, pk=None):
        """
        Retrieve user requests for a specific elevator.
        Params:
        - pk: Elevator ID.
        Returns:
        - Response: Serialized user requests.
        Example: GET /get_user_requests/1/
        Response: [{"requested_floor": 2, "destination_floor": 6, "is_complete": false, "created_at": "2023-01-01T12:00:00Z"}, ...]
        """
        # user_requests_cache = redis_client.get(f'user_requests_{pk}')
        # if user_requests_cache:
        #     return Response(json.loads(user_requests_cache))
        elevator = get_object_or_404(Elevator, pk=pk)
        requests = UserRequest.objects.filter(elevator=elevator)
        serializer = UserRequestSerializer(requests, many=True)
        # user_requests_data = serializer.data
        # redis_client.set(f'user_requests_{pk}', json.dumps(user_requests_data), ex=3600)
        return Response(serializer.data)


    @action(detail=True, methods=["get"])
    def get_next_floor(self, request, pk=None):
        """
        API to retrieve the next destination floor for a specific elevator.
        Params:
        - pk: Elevator ID.
        Returns:
        - JsonResponse: Success message and next destination floor.
        Example: GET /get_next_floor/1/
        Response: {"message": "Next floor retrieved successfully.", "elevator_id": 1, "next_floor": 7}
        """
        elevator = get_object_or_404(Elevator, pk=pk)
        current_floor = elevator.current_floor
        request = (
            UserRequest.objects.filter(elevator=elevator, is_complete=False)
            .order_by("created_at")
            .first()
        )
        if not request:
            return Response(
                {"error": "No requests found for the elevator."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        requested_from_floor = request.requested_floor
        requested_to_floor = request.destination_floor
        next_floor = (
            requested_to_floor
            if current_floor == requested_from_floor
            else requested_from_floor
        )
        return JsonResponse(
            {
                "message": "Next floor retrieved successfully.",
                "elevator_id": elevator.pk,
                "next_floor": next_floor,
            },
            status=status.HTTP_200_OK,
        )


    @action(detail=True, methods=["get"])
    def check_direction(self, request, pk=None):
        """
        API to check the direction of a specific elevator.
        Params:
        - pk: Elevator ID.
        Returns:
        - JsonResponse: Success message and elevator direction.
        Example: GET /check_direction/1/
        Response: {"message": "Direction retrieved successfully.", "elevator_id": 1, "direction": "up"}
        """
        elevator = get_object_or_404(Elevator, pk=pk)
        if elevator.in_maintenance or elevator.is_door_open:
            return Response(
                {"error": "Elevator is in maintenance or door is open."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        current_floor = elevator.current_floor
        requests = UserRequest.objects.filter(
            elevator=elevator, is_complete=False
        ).order_by("created_at")
        if not requests:
            return Response(
                {"error": "No requests found for the elevator."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request = requests.first()
        requested_from_floor = request.requested_floor
        requested_to_floor = request.destination_floor

        if current_floor == requested_from_floor:
            next_floor = requested_to_floor
        else:
            next_floor = requested_from_floor
        if next_floor > current_floor:
            direction = "up"
        elif next_floor < current_floor:
            direction = "down"
        else:
            direction = "stationary"
        return JsonResponse(
            {
                "message": "Direction retrieved successfully.",
                "elevator_id": elevator.pk,
                "direction": direction,
            },
            status=status.HTTP_200_OK,
        )


    @action(detail=True, methods=["post"])
    def door_status(self, request, pk=None):
        """
        API to toggle the door status of a specific elevator.
        Params:
        - pk: Elevator ID.
        Returns:
        - JsonResponse: Current door status.
        Example: POST /door_status/1/
        Response: {"is_door_open": true}
        """
        try:
            elevator = self.get_object()
            elevator.door_opened = not elevator.is_door_open #Using the not operator to invert the boolean value
            elevator.save()
            return Response({'door_opened': elevator.is_door_open})
        except Elevator.DoesNotExist:
            return Response({'error': 'Elevator not found.'}, status=status.HTTP_404_NOT_FOUND)
        


    @action(detail=True, methods=["post"])
    def toggle_maintenance(self, request, pk=None):
        """
        API to toggle the maintenance status of a specific elevator.
        Params:
        - pk: Elevator ID.
        Returns:
        - Response: Success message indicating the current maintenance status.
        Example: POST /toggle_maintenance/1/
        Response: {"message": "Elevator marked as in maintenance."}
        """
        try:
            elevator = self.get_object()
            elevator.in_maintenance = not elevator.in_maintenance
            elevator.save()

            status_message = (
                "Elevator marked as in maintenance."
                if elevator.in_maintenance
                else "Elevator marked as not in maintenance."
            )
            return Response({"message": status_message})
        except Elevator.DoesNotExist:
            return JsonResponse(
                {"error": "Elevator not found."}, status=status.HTTP_404_NOT_FOUND
            )


    @action(detail=True, methods=["post"])
    def move_elevator(self, request, pk=None):
        """
        API to move a specific elevator to the requested floors.
        Params:
        - pk: Elevator ID.
        Returns:
        - JsonResponse: Success message and elevator details after the move.
        Example: POST /move_elevator/1/
        Response: {"message": "Elevator moved successfully.", "elevator_id": 1, "current_floor": 5, "previous_floor": 3}
        """
        elevator = get_object_or_404(Elevator, pk=pk)

        if elevator.in_maintenance or elevator.is_door_open:
            return Response(
                {"error": "Elevator is in maintenance or door is open."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        current_floor = elevator.current_floor
        old_floor = current_floor
        requests = UserRequest.objects.filter(
            elevator=elevator, is_complete=False
        ).order_by("created_at")

        if not requests.exists():
            return Response(
                {"error": "No more uncompleted requests found for this elevator."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        first_request = requests.first()
        if current_floor == first_request.requested_floor:
            elevator.current_floor = first_request.destination_floor
            first_request.is_complete = True
        else:
            elevator.current_floor = first_request.requested_floor
        elevator.save()
        first_request.save()
        return JsonResponse(
            {
                "message": "Elevator moved successfully.",
                "elevator_id": elevator.pk,
                "current_floor": elevator.current_floor,
                "previous_floor": old_floor,
            },
            status=status.HTTP_200_OK,
        )
