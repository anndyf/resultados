from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sistema_notas/', include('sistema_notas.urls')),  # Inclui as URLs do aplicativo sistema_notas
    # Outras URLs do projeto, se houver...
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)