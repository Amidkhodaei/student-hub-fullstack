from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
import re

class MyUserManager(BaseUserManager):
    def create_user(self, student_no, password=None, **extra_fields):
        if not student_no:
            raise ValueError('شماره دانشجویی باید وارد شود')
        
        if 'email' in extra_fields:
            extra_fields['email'] = self.normalize_email(extra_fields['email'])

        extra_fields.setdefault('is_active', False)

        user = self.model(student_no=student_no, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_no, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # سوپر یوزر باید از ابتدا فعال باشد

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(student_no, password, **extra_fields)

class User(AbstractUser):
    student_no = models.CharField(max_length=8, unique=True)
    phone = models.CharField(max_length=11, null=True, blank=True)
    email = models.EmailField(blank=False, null=False)
    is_active = models.BooleanField(default=False) # فیلد وضعیت فعال بودن

    username = None
    USERNAME_FIELD = 'student_no'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    objects = MyUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_no})"
    
class Department(models.Model):
    dept_id = models.IntegerField(unique=True)
    dept_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.dept_name
    
class Instructor(models.Model):
    instructor_name = models.CharField(max_length=50, unique=True)
    departments = models.ManyToManyField(Department, related_name='instructors')

    def __str__(self):
        return self.instructor_name
    
class Lesson(models.Model):
    GENDER_CHOICES = [
        (0, 'مختلط'),
        (1, 'مرد'),
        (2, 'زن'),
    ]
    lesson_id = models.CharField(max_length=10, unique=True)
    lesson_name = models.CharField(max_length=100)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='lessons')
    credit = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    active_credit = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(1)])
    capacity = models.IntegerField(blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)
    instructors_list = models.JSONField(default=list, blank=True, null=True)
    times = models.JSONField(default=list, blank=True, null=True)
    exam_time = models.JSONField(default=list, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def clean(self):
        if not isinstance(self.times, list):
            raise ValidationError({'times': 'فرمت زمان‌ها باید لیست باشد'})
        for idx, time_slot in enumerate(self.times):
            required_fields = ['day', 'start', 'end', 'isExerciseSolving']
            for field in required_fields:
                if field not in time_slot:
                    raise ValidationError({'times': f'زمان {idx+1}: فیلد {field} الزامی است'})
            if time_slot['day'] not in [0, 1, 2, 3, 4, 5, 6]:
                raise ValidationError({'times': f'زمان {idx+1}: روز باید بین 0 تا 6 باشد'})
            time_pattern = r'^([0-1]\d|2[0-3]):[0-5]\d$'
            if not re.match(time_pattern, str(time_slot['start'])) or not re.match(time_pattern, str(time_slot['end'])):
                raise ValidationError({'times': f'زمان {idx+1}: فرمت ساعت شروع یا پایان باید به صورت HH:MM باشد'})
            if time_slot['start'] >= time_slot['end']:
                raise ValidationError({'times': f'زمان {idx+1}: ساعت شروع باید از پایان کمتر باشد'})
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.lesson_id} - {self.lesson_name}"


class SavedSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_schedules')
    title = models.CharField(max_length=100, blank=True, default='برنامه من')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user.student_no})"


class ScheduleItem(models.Model):
    schedule = models.ForeignKey(SavedSchedule, on_delete=models.CASCADE, related_name='items')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='schedule_items')
    color = models.CharField(max_length=7, default='#248F24')  # کد رنگ هگز

    class Meta:
        unique_together = ('schedule', 'lesson')

    def __str__(self):
        return f"{self.lesson.lesson_name} @ {self.schedule.title}"