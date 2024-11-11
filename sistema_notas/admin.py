from django.contrib import admin
from django.urls import path
from .models import Turma, Estudante, Disciplina, NotaFinal, DisciplinaTurma
from .views import upload_csv
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from .forms import DisciplinaMultipleForm
from django.contrib import messages 


class EstudanteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'turma')
    search_fields = ('nome',)
    ordering = ('nome',)
    list_filter = ('turma',)

    # Template customizado para incluir o botão "Upload CSV"
    change_list_template = "admin/sistema_notas/estudante_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.upload_csv_view, name='upload-csv'),
        ]
        return custom_urls + urls

    @staff_member_required
    def upload_csv_view(self, request):
        # Redireciona para a view de upload de CSV
        return upload_csv(request)

class EstudanteInline(admin.TabularInline):
    model = Estudante
    extra = 0

class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)
    inlines = [EstudanteInline]

class DisciplinaAdmin(admin.ModelAdmin):
    form = DisciplinaMultipleForm
    list_display = ('nome', 'turma')

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            form = self.get_form(request)(request.POST)
            if form.is_valid():
                nomes = form.cleaned_data['nome']
                turmas = form.cleaned_data['turmas']
                nomes = [nome.strip() for nome in nomes.split(',')]

                # Cria cada disciplina para cada combinação de nome e turma selecionada
                for nome in nomes:
                    for turma in turmas:
                        Disciplina.objects.get_or_create(nome=nome, turma=turma)

                # Adiciona uma mensagem de sucesso e redireciona
                messages.success(request, "Disciplinas foram criadas com sucesso.")
                return redirect('admin:sistema_notas_disciplina_changelist')
        
        return super().add_view(request, form_url, extra_context)

class NotaFinalAdmin(admin.ModelAdmin):
    list_display = ('estudante', 'disciplina', 'nota', 'status')
    list_filter = ('disciplina', 'status')
    search_fields = ('estudante__nome', 'disciplina__nome')


admin.site.register(Turma, TurmaAdmin)
admin.site.register(Estudante, EstudanteAdmin)
admin.site.register(Disciplina, DisciplinaAdmin)
admin.site.register(NotaFinal, NotaFinalAdmin)
admin.site.register(DisciplinaTurma)
