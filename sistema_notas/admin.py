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
    readonly_fields = ('status',)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user  # Passa o usuário atual para o formulário
        return form

    class Media:
        js = ('/static/js/carregar_disciplinas.js',) 

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('lancar-notas/', self.admin_site.admin_view(self.lancar_notas_view), name='lancar_notas'),
        ]
        return custom_urls + urls

    def lancar_notas_view(self, request):
        if request.method == 'POST':
            form = LancaNotaPorDisciplinaForm(request.POST)
            if form.is_valid():
                disciplina = form.cleaned_data['disciplina']
                estudantes = Estudante.objects.filter(turma__disciplinas=disciplina)

                for estudante in estudantes:
                    NotaFinal.objects.get_or_create(estudante=estudante, disciplina=disciplina)

                messages.success(request, f"Notas prontas para lançamento na disciplina {disciplina}.")
                return redirect('admin:sistema_notas_notafinal_changelist')
        else:
            form = LancaNotaPorDisciplinaForm()

        return render(request, 'admin/lancar_notas.html', {'form': form, 'title': 'Lançar Notas por Disciplina'})

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['lancar_notas_url'] = reverse('admin:lancar_notas')
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Turma, TurmaAdmin)
admin.site.register(Estudante, EstudanteAdmin)
admin.site.register(Disciplina, DisciplinaAdmin)
admin.site.register(NotaFinal, NotaFinalAdmin)
admin.site.register(DisciplinaTurma)
