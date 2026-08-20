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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'organizations'


class User(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
        ('ceo', 'CEO'),
        ('support', 'Support'),
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