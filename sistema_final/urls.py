from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sistema_notas/', include('sistema_notas.urls')),  # Inclui as URLs do aplicativo sistema_notas
    # Outras URLs do projeto, se houver...
]