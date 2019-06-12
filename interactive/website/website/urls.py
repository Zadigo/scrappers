from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from website.views import HeroView, DownloadView

urlpatterns = [
    re_path(r'^dowload/(?P<token>[a-zA-Z0-9]{8}$)', DownloadView.as_view(), name='download'),
    path('', HeroView.as_view(), name='home'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
