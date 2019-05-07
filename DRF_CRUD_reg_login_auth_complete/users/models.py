from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here


class Profile(AbstractUser):

    is_verified =models.BooleanField(default=False)

    def __str__(self):
        return self.email

class UserConfirmation(models.Model):
    user = models.ForeignKey(Profile,on_delete=models.CASCADE)
    token = models.CharField(max_length=255)





# Create your models here.
