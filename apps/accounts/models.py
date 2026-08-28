from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Organization(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    org_name = models.CharField(max_length=200)
    ceo_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    telegram_chat_id = models.CharField(max_length=50, blank=True)
    avatar = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='active')
    # UI preferences (avval brauzer localStorage'da saqlanardi — endi
    # hisobga bog'liq bo'lgani uchun backend'da, shunda foydalanuvchi
    # qaysi qurilma/brauzerdan kirmasin bir xil ko'rinishni ko'radi).
    theme = models.CharField(max_length=10, default='light')
    sidebar_collapsed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def organization_id(self):
        # CEO login qilganda request.user shu Organization obyekti bo'ladi
        # (User emas). Butun kodda request.user.organization_id ishlatilgani
        # uchun bu property CEO holatida ham xuddi shu ishlashini ta'minlaydi.
        return self.id

    class Meta:
        db_table = 'organizations'


class User(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),        # DEPRECATED: yangi xodim yaratishda endi tanlab bo'lmaydi,
                                        # faqat mavjud (eski) yozuvlar ishlashda davom etishi uchun saqlanadi.
        ('manager', 'Manager'),        # DEPRECATED: yuqoridagi bilan bir xil sabab.
        ('admin', 'Admin'),
        ('ceo', 'CEO'),
        ('support', 'Support'),        # Platforma darajasidagi (global) Support — barcha tashkilotlarni ko'radi.
        ('org_support', 'Support'),    # CEO/Admin o'z tashkilotiga yarata oladigan tashkilot darajasidagi
                                        # Support xodimi. MUHIM: ataylab 'support'dan FARQLI qiymat — chunki
                                        # 'support' butun kod bo'ylab platforma-darajasidagi (barcha
                                        # tashkilotlarni ko'ra oladigan) huquqni bildiradi. Agar xodimga xuddi
                                        # shu 'support' qiymati berilsa, u CEO o'z tashkilotiga yaratgan oddiy
                                        # xodim bo'lgani holda, boshqa BARCHA tashkilotlarning ma'lumotlarini
                                        # ko'ra oladigan bo'lib qolardi (jiddiy xavfsizlik muammosi).
    )

    id = models.CharField(max_length=50, primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telegram_chat_id = models.CharField(max_length=50, blank=True)
    avatar = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='active')
    group = models.ForeignKey('exams.Group', null=True, blank=True, on_delete=models.SET_NULL)
    # UI preferences (avval brauzer localStorage'da saqlanardi — endi
    # hisobga bog'liq bo'lgani uchun backend'da, shunda foydalanuvchi
    # qaysi qurilma/brauzerdan kirmasin bir xil ko'rinishni ko'radi).
    theme = models.CharField(max_length=10, default='light')
    sidebar_collapsed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'users'


class SupportTicket(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    user_name = models.CharField(max_length=100)
    user_role = models.CharField(max_length=50)
    org_name = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'support_tickets'