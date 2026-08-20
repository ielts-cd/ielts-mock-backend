from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamResultViewSet

router = DefaultRouter()
router.register(r'', ExamResultViewSet, basename='result')

urlpatterns = [
    path('', include(router.urls)),
]