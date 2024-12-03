from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from apps.authkit.manager import UserManager
from apps.base.base_model import BaseModel

class Batch(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.name}"

#==== User Model ====#
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Student', 'Student'),
        ('Faculty', 'Faculty'),
    )
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, blank=True, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']
    
    def __str__(self):
        return f'Username: {self.username}'
    
    