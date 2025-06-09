from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('custas/', include('app_custas.urls')), # Inclui as URLs da sua app
]
