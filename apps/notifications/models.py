from django.db import models
from apps.accounts.models import Organization


class Message(models.Model):
    """
    Ichki xabar tizimi (Support <-> CEO, CEO -> Employee/Student).

    Mavjud SupportTicket modelidagi kabi (apps.accounts.models) sender/recipient
    ma'lumotlari DENORMALIZATSIYA qilingan holda saqlanadi (id + role + name),
    chunki jo'natuvchi/qabul qiluvchi ikkita turli modelga tegishli bo'lishi
    mumkin: Organization (CEO) yoki User (Support/Employee/Student) — bitta
    umumiy ForeignKey ikkalasiga ham ishora qila olmaydi.

    "Barcha CEO'larga" yoki "bir nechta xodim/o'quvchi"ga yuborilganda —
    HAR BIR qabul qiluvchi uchun ALOHIDA Message qatori yaratiladi (fan-out).
    Shu tufayli har bir qabul qiluvchining o'z holati (sent/read/ignored)
    mustaqil kuzatiladi va Support/CEO xabar statusini har bir kishi bo'yicha
    ko'ra oladi.
    """

    STATUS_CHOICES = (
        ('sent', 'Yuborilgan'),
        ('read', "O'qilgan"),
        ('ignored', "E'tiborsiz qoldirilgan"),
    )

    SENDER_ROLE_CHOICES = (
        ('support', 'Support'),
        ('ceo', 'CEO'),
        ('admin', 'Admin'),  # YANGI: Admin endi CEO bilan bir xil huquqda
                              # o'z tashkilotidagi xodim/o'quvchiga xabar yubora oladi.
    )

    RECIPIENT_ROLE_CHOICES = (
        ('ceo', 'CEO'),
        ('admin', 'Admin'),
        ('student', 'Student'),
    )

    id = models.CharField(max_length=50, primary_key=True)

    sender_role = models.CharField(max_length=20, choices=SENDER_ROLE_CHOICES)
    # Support uchun User.id, CEO uchun Organization.id
    sender_id = models.CharField(max_length=50)
    sender_name = models.CharField(max_length=150, blank=True)

    recipient_role = models.CharField(max_length=20, choices=RECIPIENT_ROLE_CHOICES)
    # CEO uchun Organization.id, boshqa (admin/manager/teacher/student) uchun User.id
    recipient_id = models.CharField(max_length=50)
    recipient_name = models.CharField(max_length=150, blank=True)

    # Xabar tegishli bo'lgan tashkilot — Support->CEO xabarida shu CEO'ning
    # tashkiloti, CEO->Employee/Student xabarida esa yuboruvchi CEO'ning O'ZI
    # (chunki CEO auth qilganda request.user = Organization). Ruxsat
    # tekshiruvlari (masalan CEO faqat o'z tashkilotiga) shu maydonga tayanadi.
    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name='messages'
    )

    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')

    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient_role', 'recipient_id', 'status']),
            models.Index(fields=['sender_role', 'sender_id']),
        ]