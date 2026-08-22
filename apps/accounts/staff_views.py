from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import User
from .serializers import UserSerializer
from .permissions import IsSupport, IsAdmin

class IsAdminOrSupport(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ['ceo', 'admin', 'support'])

class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    # MUHIM: Support ham (istalgan tashkilotning) xodimlar ro'yxatini ko'ra
    # olishi kerak (masalan "Tashkilotlar" panelidagi xodimlar modali uchun) —
    # avval faqat IsAdmin (ceo|admin) ruxsat berilgan edi, Support esa 403
    # olardi, garchi get_queryset() pastda uni to'g'ri hisobga olsa ham.
    permission_classes = [IsAuthenticated, IsAdminOrSupport]
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
        # Support istalgan tashkilotga xodim qo'sha oladi — shu holatda
        # so'rovda aniq "organization" (tashkilot ID) yuborilishi kerak.
        # CEO/Admin esa doim faqat O'Z tashkilotiga qo'sha oladi (xavfsizlik
        # uchun so'rovdan kelgan qiymat e'tiborga olinmaydi).
        if self.request.user.role == 'support':
            org_id = self.request.data.get('organization') or self.request.data.get('orgId')
            serializer.save(organization_id=org_id)
        else:
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