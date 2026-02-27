from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, student_no, password=None, **extra_fields):
        if not student_no:
            raise ValueError('شماره دانشجویی باید وارد شود')
        
        if 'email' in extra_fields:
            extra_fields['email'] = self.normalize_email(extra_fields['email'])

        user = self.model(student_no=student_no, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_no, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(student_no, password, **extra_fields)

class User(AbstractUser):
    student_no = models.CharField(max_length=8, unique=True)
    phone = models.CharField(max_length=11, null=True, blank=True)
    email = models.EmailField(blank=False, null=False)

    username = None
    USERNAME_FIELD = 'student_no'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    objects = MyUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_no})"