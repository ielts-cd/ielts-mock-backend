from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .ticket_views import SupportTicketViewSet

router = DefaultRouter()
router.register(r'', SupportTicketViewSet, basename='support-ticket')

urlpatterns = [
    path('', include(router.urls)),
]