"""
URL configuration for cattle_disease_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('landing.urls')),
    path('accounts/', include('accounts.urls')),
    path('farmers/', include('farmers.urls')),
    path('vets/', include('vets.urls')),
    path('ministry/', include('ministry.urls')),
    path('cases/', include('cases.urls')),
    path('maps/', include('maps.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
