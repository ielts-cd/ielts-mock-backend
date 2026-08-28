from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import User
from .serializers import StaffSerializer
from .permissions import IsSupport, IsAdmin

class IsAdminOrSupport(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ['ceo', 'admin', 'support'])

# Ro'yxatdagi mavjud (eski) xodim rollari — 'manager'/'teacher' DEPRECATED:
# yangi xodim endi shu rollar bilan yaratilmaydi (StaffSerializer buni
# taqiqlaydi), lekin ilgari yaratilgan xodimlar ro'yxatdan tushib
# ketmasligi/ishlashda davom etishi uchun queryset filtrida saqlanadi.
STAFF_ROLES = ['admin', 'org_support', 'manager', 'teacher']

class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = StaffSerializer
    # MUHIM: Support ham (istalgan tashkilotning) xodimlar ro'yxatini ko'ra
    # olishi kerak (masalan "Tashkilotlar" panelidagi xodimlar modali uchun) —
    # avval faqat IsAdmin (ceo|admin) ruxsat berilgan edi, Support esa 403
    # olardi, garchi get_queryset() pastda uni to'g'ri hisobga olsa ham.
    # Lekin YANGI XODIM YARATISH (create) — endi faqat CEO/Admin uchun,
    # Support xodim yarata olmasligi kerak (get_permissions() pastda buni
    # ta'minlaydi).
    permission_classes = [IsAuthenticated, IsAdminOrSupport]
    search_fields = ['name', 'username']
    filterset_fields = ['role', 'status']

    def get_permissions(self):
        if self.action == 'create':
            # Faqat CEO va Admin xodim yarata oladi — Support bu yerga
            # umuman kirmaydi (403 qaytadi), garchi ro'yxatni ko'rish uchun
            # IsAdminOrSupport orqali ruxsati bo'lsa ham.
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsAdminOrSupport()]

    def get_queryset(self):
        if self.request.user.role == 'support':
            return User.objects.filter(role__in=STAFF_ROLES)
        return User.objects.filter(
            role__in=STAFF_ROLES,
            organization_id=self.request.user.organization_id
        )

    def perform_create(self, serializer):
        # MUHIM: bu nuqtaga endi faqat CEO yoki Admin yeta oladi (get_permissions()
        # 'create' amalini IsAdmin bilan cheklaydi, Support bu yerga hech qachon
        # yetib kelmaydi) — shu sabab har doim so'rovchining O'Z tashkilotiga
        # biriktiriladi (xavfsizlik uchun so'rovdan kelgan "organization"
        # qiymati e'tiborga olinmaydi).
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