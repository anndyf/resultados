from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.contrib import messages
from django import forms
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from .models import Turma, Estudante, Disciplina, NotaFinal, DisciplinaTurma
from .views import upload_csv
from .forms import DisciplinaMultipleForm, LancarNotasForm, NotaFinalForm

# Formulário para selecionar a disciplina e lançar notas para os estudantes associados
class LancaNotaPorDisciplinaForm(forms.Form):
    disciplina = forms.ModelChoiceField(queryset=Disciplina.objects.all(), required=True, label="Disciplina")

# Inline para exibir e lançar notas dos estudantes em uma disciplina específica
class NotaFinalInline(admin.TabularInline):
    model = NotaFinal
    extra = 0
    fields = ('estudante', 'nota', 'status')
    readonly_fields = ('estudante',)

# Configuração de EstudanteAdmin para exibir notas como inline
class EstudanteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'turma')
    search_fields = ('nome',)
    ordering = ('nome',)
    list_filter = ('turma',)
    inlines = [NotaFinalInline]
    change_list_template = "admin/sistema_notas/estudante_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.upload_csv_view, name='upload-csv'),
        ]
        return custom_urls + urls

    @staff_member_required
    def upload_csv_view(self, request):
        return upload_csv(request)

# Configuração de TurmaAdmin com inline de estudantes
class EstudanteInline(admin.TabularInline):
    model = Estudante
    extra = 0

class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)
    inlines = [EstudanteInline]

# Configuração de DisciplinaAdmin com criação de múltiplas disciplinas
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

                for nome in nomes:
                    for turma in turmas:
                        Disciplina.objects.get_or_create(nome=nome, turma=turma)

                messages.success(request, "Disciplinas foram criadas com sucesso.")
                return redirect('admin:sistema_notas_disciplina_changelist')
        
        return super().add_view(request, form_url, extra_context)

# Configuração do admin para NotaFinal com botão para lançar notas por disciplina
class NotaFinalAdmin(admin.ModelAdmin):
    form = NotaFinalForm
    list_display = ('estudante', 'disciplina', 'nota', 'status')
    list_filter = ('disciplina__turma', 'disciplina')
    list_editable = ('nota',)
    readonly_fields = ('status',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'lancar-notas-turma/',
                self.admin_site.admin_view(self.lancar_notas_turma_view),
                name='lancar_notas_turma'
            ),
        ]
        return custom_urls + urls

    def lancar_notas_turma_view(self, request):
        turmas = Turma.objects.all()
        disciplinas = []
        estudantes_com_dados = []

        turma_id = request.GET.get('turma')
        disciplina_id = request.GET.get('disciplina')

        if turma_id:
            disciplinas = Disciplina.objects.filter(turma_id=turma_id)

        if turma_id and disciplina_id:
            estudantes = Estudante.objects.filter(turma_id=turma_id)
            for estudante in estudantes:
                nota_final = NotaFinal.objects.filter(estudante=estudante, disciplina_id=disciplina_id).first()
                estudantes_com_dados.append({
                    'id': estudante.id,
                    'nome': estudante.nome,
                    'nota': nota_final.nota if nota_final else "Sem nota",
                    'status': nota_final.status if nota_final else "Sem status",
                })

        if request.method == 'POST':
            for estudante in estudantes:
                nota = request.POST.get(f"nota_{estudante.id}")
                if nota:
                    try:
                        # Substituir vírgula por ponto antes de converter
                        nota_float = float(nota.replace(',', '.'))
                        NotaFinal.objects.update_or_create(
                            estudante=estudante,
                            disciplina_id=disciplina_id,
                            defaults={'nota': nota_float},
                        )
                    except ValueError:
                        messages.error(request, f"Nota inválida para o estudante {estudante.nome}: {nota}")
                        continue

            messages.success(request, "Notas salvas com sucesso!")
            return redirect('admin:sistema_notas_notafinal_changelist')

        return render(request, 'admin/sistema_notas/notafinal/lancar-notas-turma.html', {
            'title': 'Lançar Notas por Turma',
            'turmas': turmas,
            'disciplinas': disciplinas,
            'estudantes_com_dados': estudantes_com_dados,
            'turma_id': turma_id,
            'disciplina_id': disciplina_id,
    })
    def changelist_view(self, request, extra_context=None):
        """
        Adiciona o botão de Lançar Notas por Turma na página principal.
        """
        extra_context = extra_context or {}
        extra_context['lancar_notas_turma_url'] = reverse('admin:lancar_notas_turma')
        return super().changelist_view(request, extra_context=extra_context)
admin.site.register(Turma, TurmaAdmin)
admin.site.register(Estudante, EstudanteAdmin)
admin.site.register(Disciplina, DisciplinaAdmin)
admin.site.register(NotaFinal, NotaFinalAdmin)
admin.site.register(DisciplinaTurma)
