from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.contrib import messages
from django import forms
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from .models import Turma, Estudante, Disciplina, NotaFinal, DisciplinaTurma
from .views import upload_csv
from .forms import DisciplinaMultipleForm, NotaFinalForm


# Formulário para selecionar a turma e disciplina
class LancarNotasForm(forms.Form):
    turma = forms.ModelChoiceField(queryset=Turma.objects.all(), label="Turma")
    disciplina = forms.ModelChoiceField(queryset=Disciplina.objects.none(), label="Disciplina")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'turma' in self.data:
            try:
                turma_id = int(self.data.get('turma'))
                self.fields['disciplina'].queryset = Disciplina.objects.filter(turmas=turma_id)
            except (ValueError, TypeError):
                pass


# Inline para exibir estudantes por turma
class EstudanteInline(admin.TabularInline):
    model = Estudante
    extra = 0
    fields = ('nome',)
    readonly_fields = ('nome',)


# Configuração de EstudanteAdmin para exibição no painel administrativo
class EstudanteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'turma')
    search_fields = ('nome',)
    ordering = ('nome',)
    list_filter = ('turma',)


# Configuração de TurmaAdmin com inline de estudantes
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


# Configuração do admin para NotaFinal com botão para lançar notas por turma
class NotaFinalAdmin(admin.ModelAdmin):
    list_display = ('estudante', 'disciplina', 'nota', 'status')
    list_filter = ('disciplina__turma', 'disciplina')
    readonly_fields = ('status',)  # Campo status somente leitura
    fields = ('estudante', 'disciplina', 'nota', 'status')  # Define a ordem dos campos

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('lancar-notas/', self.admin_site.admin_view(self.lancar_notas_view), name='lancar_notas'),
        ]
        return custom_urls + urls

    def lancar_notas_view(self, request):
        if request.method == 'POST':
            form = LancarNotasForm(request.POST)
            if form.is_valid():
                turma = form.cleaned_data['turma']
                disciplina = form.cleaned_data['disciplina']
                estudantes = Estudante.objects.filter(turma=turma)

                # Lança notas para todos os estudantes da turma
                for estudante in estudantes:
                    NotaFinal.objects.get_or_create(
                        estudante=estudante,
                        disciplina=disciplina,
                        defaults={'nota': 0},  # Nota padrão inicial
                    )

                messages.success(
                    request, f"Notas lançadas para {len(estudantes)} estudantes da turma {turma.nome}."
                )
                return redirect('admin:sistema_notas_notafinal_changelist')
        else:
            form = LancarNotasForm()

        return render(request, 'admin/lancar_notas.html', {'form': form, 'title': 'Lançar Notas por Turma'})

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['lancar_notas_url'] = reverse('admin:lancar_notas')
        return super().changelist_view(request, extra_context=extra_context)


# Registro no painel administrativo
admin.site.register(Turma, TurmaAdmin)
admin.site.register(Estudante, EstudanteAdmin)  # Registro corrigido
admin.site.register(Disciplina, DisciplinaAdmin)
admin.site.register(NotaFinal, NotaFinalAdmin)

# Personalização do painel de administração
admin.site.site_header = "EduClass - CETEP/LNAB"
admin.site.site_title = "Administração do Sistema de Notas"
admin.site.index_title = "Bem-vindo ao Painel de Administração"
