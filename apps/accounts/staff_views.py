from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from .permissions import IsSupport, IsAdmin

class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    search_fields = ['name', 'username']
    filterset_fields = ['role', 'status']

    def get_queryset(self):
        if self.request.user.role == 'support':
            return User.objects.filter(role__in=['admin', 'manager', 'teacher'])
        return User.objects.filter(
            role__in=['admin', 'manager', 'teacher'],
            organization_id=self.request.user.organization_id
        )

    def perform_create(self, serializer):
        serializer.save(organization_id=self.request.user.organization_id)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        staff = self.get_object()
        status_val = request.data.get('status')
        if status_val not in ['active', 'inactive']:
            return Response({'success': False, 'message': 'Invalid status'},
                          status=status.HTTP_400_BAD_REQUEST)
        staff.status = status_val
        staff.save()
        return Response({'success': True, 'status': staff.status})