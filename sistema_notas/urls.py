from django.urls import path
from . import views
from .views import DisciplinaAutocomplete, EstudanteAutocomplete

urlpatterns = [
    path('turma/<int:turma_id>/status/', views.listar_status_turma, name='listar_status_turma'),
    path('carregar-disciplinas/', views.carregar_disciplinas, name='carregar_disciplinas'),
    path('admin/sistema_notas/upload-csv/', views.upload_csv, name='upload_csv'),
    path('carregar-disciplinas/', views.carregar_disciplinas, name='carregar_disciplinas'),
    path('disciplina-autocomplete/', DisciplinaAutocomplete.as_view(), name='disciplina-autocomplete'),
    path('estudante-autocomplete/', EstudanteAutocomplete.as_view(), name='estudante-autocomplete'),

]
