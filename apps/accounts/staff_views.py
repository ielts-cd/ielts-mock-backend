from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import User
from .serializers import StaffSerializer

class IsCeoOrSupport(BasePermission):
    """
    Xodim (Admin hisobi) YARATISH — FAQAT CEO (o'z tashkilotiga) va Support
    (istalgan tashkilotga) uchun. Admin YANGI XODIM (yoki umuman boshqa
    foydalanuvchi) YARATA OLMAYDI — bu yagona farq, boshqa hamma narsada
    (ko'rish/tahrirlash/o'chirish) Admin CEO bilan bir xil huquqqa ega
    (pastdagi IsStaffManager'ga qarang).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ['ceo', 'support'])

class IsStaffManager(BasePermission):
    """
    Xodimlar ro'yxatini KO'RISH/TAHRIRLASH/O'CHIRISH — CEO, Admin va Support
    uchun bir xil (parity: "CEOda nima bo'lsa, Adminda ham xuddi shunday").
    Faqat YARATISH (create action) bundan mustasno — u yuqoridagi
    IsCeoOrSupport bilan alohida cheklanadi (get_permissions()ga qarang).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ['ceo', 'admin', 'support'])

# Xodim (organization employee) darajasidagi yagona rol — endi faqat 'admin'.
# ('teacher'/'manager'/'org_support' rollari butunlay olib tashlandi;
# 0005_migrate_legacy_roles_to_admin migratsiyasi mavjud bazadagi bunday
# yozuvlarni ham "admin"ga o'tkazgan, shu sabab bu yerda ularni alohida
# hisobga olishning hojati yo'q.)
STAFF_ROLES = ['admin']

class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = StaffSerializer
    search_fields = ['name', 'username']
    filterset_fields = ['role', 'status']

    def get_permissions(self):
        # MUHIM: faqat "create" (yangi xodim yaratish) CEO/Support bilan
        # cheklanadi — Admin bu amalga hech qachon ruxsat ololmaydi. Boshqa
        # barcha amallar (list/retrieve/update/partial_update/destroy/status)
        # uchun Admin ham CEO bilan bir xil ruxsatga ega.
        if self.action == 'create':
            return [IsAuthenticated(), IsCeoOrSupport()]
        return [IsAuthenticated(), IsStaffManager()]

    def get_queryset(self):
        # MUHIM: 'support' roli bu yerda ATAYLAB STAFF_ROLES'ga kiritilmagan —
        # shu sabab Support hisoblari bu ro'yxatda (demak update/destroy orqali
        # ham) HECH QACHON ko'rinmaydi, hatto boshqa Support foydalanuvchisi
        # so'rasa ham ("Support accountini hech kim o'zgartira/o'chira olmasin").
        if self.request.user.role == 'support':
            return User.objects.filter(role__in=STAFF_ROLES)
        return User.objects.filter(
            role__in=STAFF_ROLES,
            organization_id=self.request.user.organization_id
        )

    def perform_create(self, serializer):
        # Bu metodga endi FAQAT CEO yoki Support yeta oladi (get_permissions()
        # 'create'ni IsCeoOrSupport bilan cheklaydi, Admin bu yerga hech qachon
        # yetib kelmaydi).
        # CEO — doim FAQAT o'z tashkilotiga xodim qo'sha oladi (xavfsizlik
        # uchun so'rovdan kelgan "organization" qiymati e'tiborga olinmaydi).
        # Support — istalgan tashkilotga xodim qo'sha oladi, lekin qaysi
        # tashkilotga tegishli ekanligi so'rovda ANIQ ko'rsatilishi shart.
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