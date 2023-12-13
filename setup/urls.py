from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('teacher/', include("apps.teachers.urls")),
    path('student/', include("apps.students.urls")),
    path('', include('apps.users.urls'))
]


