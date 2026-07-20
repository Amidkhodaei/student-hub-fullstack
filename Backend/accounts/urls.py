from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, DepartmentViewSet, InstructorViewSet, LessonViewSet, UploadLessonsExcelView, SavedScheduleViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, 'x')
router.register(r'department', DepartmentViewSet, basename='department')
router.register(r'instructors', InstructorViewSet, basename='instructor')
router.register(r'lessons', LessonViewSet,basename='lesson')
router.register(r'schedules', SavedScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
    path('upload-lessons/', UploadLessonsExcelView.as_view(), name='upload-lessons'),
]