from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator

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
    
class Department(models.Model):
    dept_id = models.IntegerField(unique=True)
    dept_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.dept_name
    
class Instructor(models.Model):
    instructor_name = models.CharField(max_length=50)
    departments = models.ManyToManyField(Department, related_name='instructors')

    def __str__(self):
        return self.instructor_name
    
class Lesson(models.Model):
    GENDER_CHOICES = [
        (0, 'مختلط'),
        (1, 'مرد'),
        (2, 'زن'),
    ]
    DAY_CHOICES = [
        (0, 'شنبه'),
        (1, 'یکشنبه'),
        (2, 'دوشنبه'),
        (3, 'سه‌شنبه'),
        (4, 'چهارشنبه'),
        (5, 'پنجشنبه'),
        (6, 'جمعه'),
    ]
    lesson_id = models.CharField(max_length=10, unique=True)
    lesson_name = models.CharField(max_length=100)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='lessons')
    credit = models.IntegerField(validators=[
        MinValueValidator(0, message="Invalid Credit"),
        MaxValueValidator(4, message="Invalid Credit")
    ])
    active_credit = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(0, message="Invalid Credit"),
            MaxValueValidator(1, message="Invalid Credit")
        ]
    )
    capacity = models.IntegerField()
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)
    instructors_list = models.JSONField(default=list, blank=True, null=True)
    times = models.JSONField(default=list)
    exam_time = models.JSONField(default=list, blank=True, null=True)
    description = models.TextField()

    def clean(self):
        """اعتبارسنجی زمان‌ها"""
        if not isinstance(self.times, list):
            raise ValidationError({'times': 'فرمت زمان‌ها باید لیست باشد'})
        
        for idx, time_slot in enumerate(self.times):
            # بررسی وجود فیلدهای required
            required_fields = ['day', 'start', 'end', 'isExerciseSolving']
            for field in required_fields:
                if field not in time_slot:
                    raise ValidationError({
                        'times': f'زمان {idx+1}: فیلد {field} الزامی است'
                    })
            
            # بررسی روز
            if time_slot['day'] not in [0, 1, 2, 3, 4, 5, 6]:
                raise ValidationError({
                    'times': f'زمان {idx+1}: روز باید بین 0 تا 6 باشد'
                })
            
            # بررسی زمان شروع و پایان
            if time_slot['start'] < 0 or time_slot['start'] > 23:
                raise ValidationError({
                    'times': f'زمان {idx+1}: ساعت شروع باید بین 0 تا 23 باشد'
                })
            
            if time_slot['end'] < 0 or time_slot['end'] > 23:
                raise ValidationError({
                    'times': f'زمان {idx+1}: ساعت پایان باید بین 0 تا 23 باشد'
                })
            
            if time_slot['start'] >= time_slot['end']:
                raise ValidationError({
                    'times': f'زمان {idx+1}: ساعت شروع باید از پایان کمتر باشد'
                })
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.lesson_id} - {self.lesson_name}" 
    