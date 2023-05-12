from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PrimaryUser(User):
    staff_number = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.first_name