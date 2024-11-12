from django.urls import path
from . import views

urlpatterns = [
    path('turma/<int:turma_id>/status/', views.listar_status_turma, name='listar_status_turma'),
    path('carregar-disciplinas/', views.carregar_disciplinas, name='carregar_disciplinas'),
    path('disciplina-autocomplete/', views.DisciplinaAutocomplete.as_view(), name='disciplina-autocomplete'),
    path('admin/sistema_notas/upload-csv/', views.upload_csv, name='upload_csv'),
    path('carregar-disciplinas/', views.carregar_disciplinas, name='carregar_disciplinas'),
    path('disciplina-autocomplete/', views.DisciplinaAutocomplete.as_view(), name='disciplina-autocomplete'),
    path('estudante-autocomplete/', views.EstudanteAutocomplete.as_view(), name='estudante-autocomplete'),
]
