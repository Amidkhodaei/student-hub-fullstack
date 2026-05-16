from django.contrib import admin
from .models import User, Department, Instructor, Lesson

# Register your models here.
admin.site.register(User)
admin.site.register(Department)
admin.site.register(Instructor)
admin.site.register(Lesson)