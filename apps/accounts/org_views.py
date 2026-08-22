from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Organization
from .serializers import OrganizationSerializer
from .permissions import IsSupport

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    search_fields = ['org_name', 'ceo_name', 'username']
    filterset_fields = ['status']

    def get_permissions(self):
        # Ro'yxatni ko'rish/yaratish/o'chirish/holatini o'zgartirish — faqat
        # Support (platforma darajasida boshqaradi). Lekin CEO/Admin o'z
        # tashkilotining profilini (nom/email/Telegram Chat ID/parol) shu
        # endpoint orqali TAHRIRLASHI kerak (masalan profil sahifasidan) —
        # shu sabab retrieve/update/partial_update uchun IsAuthenticated
        # yetarli, aniqroq tekshiruv get_queryset/get_object darajasida.
        if self.action in ['list', 'create', 'destroy', 'status']:
            return [IsAuthenticated(), IsSupport()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.role == 'support':
            return Organization.objects.all()
        if self.request.user.role in ['ceo', 'admin'] and self.request.user.organization_id:
            return Organization.objects.filter(id=self.request.user.organization_id)
        return Organization.objects.none()

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