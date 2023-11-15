from django.urls import path,include
from Elevator_app.views import ElevatorViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'elevators',ElevatorViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('initialize_system/', ElevatorViewSet.as_view({'post': 'initialize_system'}), name='initialize_system'),
    path('save_request/', ElevatorViewSet.as_view({'post': 'save_request'}), name='save_request'),
] 