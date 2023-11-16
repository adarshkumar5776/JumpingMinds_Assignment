from django.urls import path,include
from Elevator_app.views import ElevatorViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'elevators',ElevatorViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('initialize_elevators/', ElevatorViewSet.as_view({'post': 'initialize_system'}), name='initialize_system'),
    path('save_user_request/', ElevatorViewSet.as_view({'post': 'save_request'}), name='save_request'),
    path('<int:pk>/get_requests/', ElevatorViewSet.as_view({'get': 'get_requests'}), name='elevator-get-requests'),
    path('<int:pk>/get_next_floor/', ElevatorViewSet.as_view({'get': 'get_next_floor'}), name='get_next_floor'),
    path('<int:pk>/check_direction/', ElevatorViewSet.as_view({'get': 'direction'}), name='direction'),
    path('<int:pk>/toggle_door/', ElevatorViewSet.as_view({'post': 'toggle_door'}), name='elevator-toggle-door'),
    path('<int:pk>/toggle_maintenance/', ElevatorViewSet.as_view({'post': 'toggle_maintenance'}), name='elevator-toggle-maintenance'),
    path('<int:pk>/move_elevator/', ElevatorViewSet.as_view({'post': 'move_elevator'}), name='elevator-move'),
] 