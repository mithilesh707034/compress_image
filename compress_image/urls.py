from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib import admin
from mainApp.views import home_page
from mainApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home_page'),
    path('remove-watermark', views.remove_watermark, name='remove_watermark'),
    path('send/', views.send_auto_bulk_whatsapp_message, name='send_auto_bulk_whatsapp_message'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
