from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=settings.MEDIA_URL + 'profile/logo.jpg', permanent=True)),
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
    path('blog/', include('blog.urls')),
    path('books/', include('books.urls')),
    path('tasks/', include('time_tracker.urls')),
    path('pins/', include('pin_interast.urls')),
    path('pin-interast/', RedirectView.as_view(url='/pins/', permanent=False)),
    path('pin-interast/<path:extra>', RedirectView.as_view(url='/pins/%(extra)s', permanent=False)),
]

# Always serve media files locally (profile photos, skills icons, etc.)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler400 = 'portfolio.views.bad_request'
handler403 = 'portfolio.views.permission_denied'
handler404 = 'portfolio.views.page_not_found'
handler500 = 'portfolio.views.server_error'
