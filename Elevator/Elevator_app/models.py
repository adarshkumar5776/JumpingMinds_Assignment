from django.db import models

# Create your models here.
class Elevator(models.Model):
    current_floor = models.IntegerField(default=1)
    is_door_open = models.BooleanField(default=False)
    in_maintenance = models.BooleanField(default=False)
    direction = models.IntegerField(default=0)

    def __str__(self):
        return f"Elevator {self.pk}" 
    
class UserRequest(models.Model):
    elevator = models.ForeignKey(Elevator, on_delete=models.CASCADE, related_name='requests')
    requested_floor = models.IntegerField(blank=True, null=True)
    current_floor = models.IntegerField(blank=True, null=True)
    destination_floor = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Request {self.pk} for Elevator {self.elevator.pk}" 