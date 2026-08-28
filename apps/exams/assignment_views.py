from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Assignment
from .serializers import AssignmentSerializer
from apps.accounts.permissions import IsOrganizationMember


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    search_fields = ['title']

    def get_queryset(self):
        if self.request.user.role == 'support':
            return Assignment.objects.all()
        if self.request.user.role in ['ceo', 'admin', 'manager', 'teacher', 'org_support']:
            return Assignment.objects.filter(organization_id=self.request.user.organization_id)
        if self.request.user.role == 'student':
            return Assignment.objects.filter(
                groups__in=[self.request.user.group_id],
                organization_id=self.request.user.organization_id
            )
        return Assignment.objects.none()

    def perform_create(self, serializer):
        assignment = serializer.save(organization_id=self.request.user.organization_id)
        # Set groups
        group_ids = self.request.data.get('groups', [])
        if group_ids:
            assignment.groups.set(group_ids)
        # Set target students
        target_ids = self.request.data.get('target_students', [])
        if target_ids:
            assignment.target_students.set(target_ids)

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        assignment = self.get_object()
        student = request.user

        if student.role != 'student':
            return Response({'success': False, 'message': 'Only students can view assignments'},
                            status=status.HTTP_403_FORBIDDEN)

        if student not in assignment.viewed_by.all():
            assignment.viewed_by.add(student)

        return Response({'success': True, 'message': 'Marked as viewed'})