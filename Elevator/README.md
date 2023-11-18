# JumpingMinds Backend Challenge

## Assignment

In this challenge, you are asked to implement the business logic for a simplified elevator model in Python using Django Rest Framework. The task involves creating an elevator system that can be initialized with N elevators and maintains the elevator states.

[Link to Assignment Document](https://docs.google.com/document/d/1ZlJKfawiwqaEy2qoa0iAOB36Y0Ph5K2_zsvLcVJJBxk/edit)

## Solution Overview

### Algorithm

The elevator allocation algorithm, within the `save_request` function, checks for available elevators without maintenance or open doors. If none are available, an error is returned. The algorithm calculates the distance from the new request's floor to the last requested floor, considering that the elevator will eventually reach this floor after completing the ongoing request. Distances and corresponding elevators are stored, sorted by distance in ascending order. The closest elevator is selected, and the user's request is associated with it. The request details, including the elevator and relevant floor information, are then saved in the database.

### Working

1-ElevatorViewSet Class:
Manages CRUD operations for Elevator objects.
Includes custom actions like initialize_elevators, save_user_request, get_user_requests, get_next_floor, check_direction, door_status, toggle_maintenance, and move_elevator.

2-initialize_elevators:
Initializes the elevator system with a specified number of elevators.

3- save_user_request:
Saves a user request and assigns the most optimal elevator based on the current state of elevators and their distances.

4-get_user_requests:
Retrieves user requests for a specific elevator.

5-get_next_floor:
Retrieves the next destination floor for a specific elevator.
6-check_direction:
Checks the direction of a specific elevator based on its current state and user requests.

7-door_status:
Toggles the door status (open or closed) of a specific elevator.

8-toggle_maintenance:
Toggles the maintenance status of a specific elevator.

9-move_elevator:
Moves a specific elevator to the requested floors, updating its current and previous floor, and marking completed requests.

### Database

PostgreSQL is used with the following configuration:

```python
'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ElevatorDB',
        'USER': 'postgres',
        'PASSWORD':'******',
        'HOST':'localhost' 
    }
```
### API

```python
> Initialize System

URL: elevators/initialize_elevators
Method: POST
Description: Initialize the elevator system with a specified number of elevators.
Request Body:
{
    "number_of_elevators": 3
}
Response:
{
    "message": "3 elevators initialized successfully.",
    "elevators": [
        {"elevator_id": 1},
        {"elevator_id": 2},
        {"elevator_id": 3}
    ]
}


## Save Request

**URL:** `/elevators/save_user_request`

**Method:** POST

**Description:** Save a user request and assign the most optimal elevator to the request.

**Request Body:**
```json
{
    "requested_floor": 3,
    "destination_floor": 7
}
 **Response Body:**
 ```json
{
    "message": "User request saved successfully.",
    "elevator_id": 1
}


## Get Requests

**URL:** `/elevators/{elevator_id}/get_user_requests`

**Method:** GET

**Description:** Fetch all requests for a given elevator.

**Response:**
```json
[
    {
        "id": 1,
        "elevator": 1,
        "requested_from_floor": 3,
        "requested_to_floor": 7,
        "created_at": "2023-07-05T10:00:00Z",
        "is_complete": false
    },
    {
        "id": 2,
        "elevator": 1,
        "requested_from_floor": 5,
        "requested_to_floor": 2,
        "created_at": "2023-07-05T10:15:00Z",
        "is_complete": false
    }
]

## Get Next Floor

**URL:** `/elevators/{elevator_id}/get_next_floor`

**Method:** GET

**Description:** Fetch the next destination floor for a given elevator.

**Response:**
```json
{
    "message": "Next floor retrieved successfully.",
    "elevator_id": 1,
    "next_floor": 7
}


## Direction

**URL:** `/elevators/{elevator_id}/direction`

**Method:** GET

**Description:** Check the direction (up, down, or stationary) of the elevator.

**Response:**
```json
{
    "message": "Direction retrieved successfully.",
    "elevator_id": 1,
    "direction": "up"
}

## Door Status

**URL:** `/elevators/{elevator_id}/door_status`

**Method:** POST

**Description:** Toggle the door of the elevator (open or closed).

**Response:**
```json
{
    "door_opened": true
}

## Toggle Maintenance

**URL:** `/elevators/{elevator_id}/toggle_maintenance`

**Method:** POST

**Description:** Toggle the maintenance status of an elevator.

**Response:**
```json
{
    "message": "Elevator marked as in maintenance."
}


## Move Elevator

 This API endpoint is used to move an elevator from its current floor to the next floor. After hitting it once, the elevator moves to the next floor, and hitting it again will move the elevator to the requested to floor. The response contains a message indicating the success of the operation, along with the elevator ID, current floor, and previous floor.

**URL:** `/api/v1/elevators/{elevator_id}/move_elevator`

**Method:** POST

**Description:** Move the elevator to the requested floors.

**Response:**
```json
{
    "message": "Elevator moved successfully.",
    "elevator_id": 1,
    "current_floor": 7,
    "previous_floor": 5
}
```