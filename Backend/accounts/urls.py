from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, DepartmentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, 'x')
router.register(r'department', DepartmentViewSet, basename='department')

urlpatterns = [
    path('', include(router.urls)),
]