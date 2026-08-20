from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import SupportTicket
from .serializers import SupportTicketSerializer
from .permissions import IsSupport

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['seen', 'user_role']
    search_fields = ['message', 'user_name']

    def get_queryset(self):
        if self.request.user.role == 'support':
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            user_name=self.request.user.name,
            user_role=self.request.user.role,
            organization=self.request.user.organization if hasattr(self.request.user, 'organization') else None,
            org_name=self.request.user.organization.org_name if self.request.user.organization else ''
        )

    @action(detail=True, methods=['put'])
    def mark_seen(self, request, pk=None):
        if request.user.role != 'support':
            return Response({'success': False, 'message': 'Permission denied'},
                          status=status.HTTP_403_FORBIDDEN)
        ticket = self.get_object()
        ticket.seen = True
        ticket.save()
        return Response({'success': True, 'message': 'Ticket marked as seen'})