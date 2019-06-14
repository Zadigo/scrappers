from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from website.views import HeroView, DownloadView, TennisView, TennisDetailView

urlpatterns = [
    re_path(r'^dowload/(?P<token>[a-zA-Z0-9]{8}$)', DownloadView.as_view(), name='download'),
    re_path(r'tennis/(?P<pk>\d+)/detail$', TennisDetailView.as_view()),
    re_path(r'tennis/(?P<pk>\d+)$', TennisDetailView.as_view(), name='tennis_detail'),
    path('tennis/', TennisView.as_view(), name='tennis'),

    path('', HeroView.as_view(), name='home'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
