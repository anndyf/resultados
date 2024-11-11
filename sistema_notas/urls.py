from django.urls import path
from . import views

urlpatterns = [
    path('turma/<int:turma_id>/status/', views.listar_status_turma, name='listar_status_turma'),
]

urlpatterns = [
    path('admin/sistema_notas/upload-csv/', views.upload_csv, name='upload_csv'),
]