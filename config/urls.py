from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import frontend

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/organizations/', include('apps.accounts.org_urls')),
    path('api/users/', include('apps.accounts.user_urls')),
    path('api/staff/', include('apps.accounts.staff_urls')),
    path('api/groups/', include('apps.exams.group_urls')),
    path('api/students/', include('apps.exams.student_urls')),
    path('api/exams/', include('apps.exams.exam_urls')),
    path('api/assignments/', include('apps.exams.assignment_urls')),
    path('api/results/', include('apps.results.urls')),
    path('api/support-tickets/', include('apps.accounts.ticket_urls')),
    path('api/messages/', include('apps.notifications.urls')),
    path('api/uploads/', include('apps.uploads.urls')),
    path('', frontend, name='frontend'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)