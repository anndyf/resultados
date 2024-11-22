from django.contrib.auth.decorators import login_required
from sistema_notas.views import redirecionar_ou_boas_vindas
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sistema_notas/', include('sistema_notas.urls')),  # URLs do app sistema_notas
    path('boas-vindas-professor/', login_required(redirecionar_ou_boas_vindas), name='boas_vindas_professor'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
