
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from config import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('interfaces.users.urls')),  # Adjust the path if your app is elsewhere.
    path('api/', include('interfaces.members.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
