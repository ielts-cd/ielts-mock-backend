from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Organization
from .serializers import OrganizationSerializer
from .permissions import IsSupport

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsSupport]
    search_fields = ['org_name', 'ceo_name', 'username']
    filterset_fields = ['status']

    def get_queryset(self):
        return Organization.objects.all()

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        org = self.get_object()
        status_val = request.data.get('status')
        if status_val not in ['active', 'inactive']:
            return Response({'success': False, 'message': 'Invalid status'},
                          status=status.HTTP_400_BAD_REQUEST)
        org.status = status_val
        org.save()
        return Response({'success': True, 'status': org.status})