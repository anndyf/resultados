from django.shortcuts import get_object_or_404
import csv
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from dal import autocomplete
from .models import Estudante, NotaFinal, Turma, Disciplina
from .forms import LancarNotasForm, UploadCSVForm
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Turma, Disciplina, Estudante, NotaFinal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Case, When, Value, CharField
# Classe para autocomplete de disciplinas no formulário
class DisciplinaAutocomplete(autocomplete.Select2QuerySetView):
    """
    Retorna disciplinas relacionadas a uma turma específica para autocomplete.
    """
    def get_queryset(self):
        print("Chamando DisciplinaAutocomplete...")
        if not self.request.user.is_authenticated:
            return Disciplina.objects.none()  # Garante que usuários não autenticados não tenham acesso
        turma_id = self.forwarded.get('turma', None)  # Obtém o ID da turma
        if turma_id:
            return Disciplina.objects.filter(turma_id=turma_id)
        return Disciplina.objects.none()

# Classe para autocomplete de estudantes no formulário
class EstudanteAutocomplete(autocomplete.Select2QuerySetView):
    """
    Retorna estudantes relacionados a uma turma e disciplina específicas para autocomplete.
    """
    def get_queryset(self):
        print("Chamando EstudanteAutocomplete...")
        if not self.request.user.is_authenticated:
            return Estudante.objects.none()
        turma_id = self.forwarded.get('turma', None)
        disciplina_id = self.forwarded.get('disciplina', None)
        if turma_id and disciplina_id:
            return Estudante.objects.filter(turma_id=turma_id)
        return Estudante.objects.none()

# View para carregar disciplinas dinamicamente com base na turma selecionada
def carregar_disciplinas(request):
    """
    Retorna uma lista de disciplinas em formato JSON para preenchimento dinâmico em formulários.
    """
    turma_id = request.GET.get('turma')
    disciplinas = Disciplina.objects.filter(turma_id=turma_id)
    data = [{'id': d.id, 'nome': d.nome} for d in disciplinas]
    return JsonResponse(data, safe=False)

# View para carregar estudantes dinamicamente com base na disciplina selecionada
def carregar_estudantes(request):
    """
    Retorna uma lista de estudantes em formato JSON para preenchimento dinâmico em formulários.
    """
    disciplina_id = request.GET.get('disciplina')
    estudantes = Estudante.objects.filter(turma__disciplinas__id=disciplina_id)
    data = [{'id': e.id, 'nome': e.nome} for e in estudantes]
    return JsonResponse(data, safe=False)

# View para listar o status dos estudantes de uma turma
def listar_status_turma(request, turma_id):
    """
    Exibe a lista de estudantes e suas notas em uma turma específica.
    """
    turma = Turma.objects.get(id=turma_id)
    estudantes = turma.estudantes.all()
    return render(request, 'sistema_notas/listar_status_turma.html', {'turma': turma, 'estudantes': estudantes})

# View para upload e processamento de arquivos CSV
def upload_csv(request):
    """
    View para fazer upload de estudantes em massa via arquivo CSV, com pré-visualização.
    """
    preview = None  # Lista para armazenar dados do arquivo CSV para pré-visualização

    if request.method == 'POST' and 'confirm_upload' not in request.POST:
        form = UploadCSVForm(request.POST, request.FILES)
        csv_file = request.FILES.get('arquivo_csv', None)
        if not csv_file:
            messages.error(request, "Nenhum arquivo foi enviado. Por favor, selecione um arquivo.")
            return redirect('upload_csv')

        if form.is_valid():
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                preview = list(reader)  # Armazena os dados para exibição

                if len(preview) > 1:
                    # Armazena os dados na sessão para confirmação posterior
                    request.session['csv_data'] = preview
                    messages.info(request, "Confirme os dados antes de prosseguir com o upload.")
                else:
                    messages.error(request, "O arquivo CSV está vazio ou no formato errado.")
            except Exception as e:
                messages.error(request, f"Erro ao processar o arquivo: {e}")
    elif request.method == 'POST' and 'confirm_upload' in request.POST:
        # Segunda etapa: Confirmação do upload
        csv_data = request.session.get('csv_data', None)
        if not csv_data:
            messages.error(request, "Nenhum arquivo foi encontrado para confirmação.")
            return redirect('upload_csv')

        duplicados_encontrados = False  # Flag para verificar duplicatas
        try:
            for row in csv_data[1:]:  # Ignora o cabeçalho
                nome_estudante = row[0].strip()
                turma_nome = row[1].strip()

                # Busca ou cria a turma
                turma, _ = Turma.objects.get_or_create(nome=turma_nome)

                # Verifica se o estudante já existe
                estudante_existente = Estudante.objects.filter(nome=nome_estudante, turma=turma).exists()
                if estudante_existente:
                    duplicados_encontrados = True
                    break  # Interrompe o processo na primeira duplicata encontrada
                else:
                    Estudante.objects.create(nome=nome_estudante, turma=turma)

            # Verifica se houve duplicatas
            if duplicados_encontrados:
                messages.error(request, "Arquivo contém estudantes já cadastrados. Por favor, envie outro arquivo.")
                return redirect('upload_csv')

            # Limpa os dados da sessão após o sucesso
            del request.session['csv_data']
            messages.success(request, "Estudantes cadastrados com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao processar o arquivo: {e}")
        return redirect('upload_csv')
    else:
        form = UploadCSVForm()

    return render(request, 'sistema_notas/upload_csv.html', {'form': form, 'preview': preview})
# View para lançar notas por turma


def grupo_professores(user):
    return user.groups.filter(name='Professores').exists()

@login_required
def redirecionar_ou_boas_vindas(request):
    """
    Redireciona professores para a página de boas-vindas após o login
    ou outros usuários para o admin.
    """
    if request.user.groups.filter(name="Professores").exists():
        return render(request, 'sistema_notas/boas_vindas_professor.html')
    return redirect('/admin/')

@user_passes_test(grupo_professores)
@login_required
@transaction.atomic
def lancar_notas_por_turma(request):
    form = LancarNotasForm(request.POST or None)
    turmas = Turma.objects.all()
    disciplinas = []
    estudantes_com_dados = []
    errors = []

    turma_id = request.GET.get('turma') or request.POST.get('turma')
    disciplina_id = request.GET.get('disciplina') or request.POST.get('disciplina')

    if turma_id:
        disciplinas = Disciplina.objects.filter(turma__id=turma_id).distinct()

    if turma_id and disciplina_id:
        estudantes = Estudante.objects.filter(turma_id=turma_id).distinct()

        # Puxa as notas atualizadas após salvar
        notas = NotaFinal.objects.filter(disciplina_id=disciplina_id, estudante__in=estudantes)
        notas_map = {nota.estudante_id: nota for nota in notas}

        for estudante in estudantes:
            nota_obj = notas_map.get(estudante.id)
            if nota_obj:
                estudantes_com_dados.append({
                    'id': estudante.id,
                    'nome': estudante.nome,
                    'nota': nota_obj.nota,
                    'status': nota_obj.status,
                    'modified_by': nota_obj.modified_by.username if nota_obj.modified_by else 'Não definido',
                    'modified_at': nota_obj.modified_at,
                })
            else:
                estudantes_com_dados.append({
                    'id': estudante.id,
                    'nome': estudante.nome,
                    'nota': None,
                    'status': "Sem status",
                    'modified_by': "Não definido",
                    'modified_at': None,
                })

    if request.method == 'POST':
        try:
            with transaction.atomic():
                for estudante_data in estudantes_com_dados:
                    nota = request.POST.get(f"nota_{estudante_data['id']}")
                    if nota:
                        try:
                            nota_float = float(nota)
                            if -1 <= nota_float <= 10:
                                # Atualiza ou cria a NotaFinal e adiciona `modified_by`
                                nota_obj, created = NotaFinal.objects.update_or_create(
                                    estudante_id=estudante_data['id'],
                                    disciplina_id=disciplina_id,
                                    defaults={'nota': nota_float},
                                )
                                # Atualiza os campos de auditoria e status
                                if nota_float == -1:
                                    nota_obj.status = "Desistente"
                                elif nota_float < 5:
                                    nota_obj.status = "Recuperação"
                                else:
                                    nota_obj.status = "Aprovado"
                                nota_obj.modified_by = request.user  # Usuário que alterou
                                nota_obj.save()
                            else:
                                errors.append(f"A nota {nota} para o estudante {estudante_data['nome']} deve estar entre -1 e 10.")
                        except ValueError:
                            errors.append(f"A nota '{nota}' fornecida para o estudante {estudante_data['nome']} é inválida.")
            if not errors:
                messages.success(request, "Notas válidas foram salvas com sucesso!")
            else:
                messages.error(request, "Algumas notas não foram salvas devido a erros.")
        except Exception as e:
            messages.error(request, f"Erro inesperado: {e}")

        # Reload page with updated data
        return redirect(f"{request.path}?turma={turma_id}&disciplina={disciplina_id}")

    return render(request, 'admin/sistema_notas/notafinal/lancar-notas-turma.html', {
        'title': 'Lançar Notas por Turma',
        'turmas': turmas,
        'disciplinas': disciplinas,
        'estudantes_com_dados': estudantes_com_dados,
        'turma_id': turma_id,
        'disciplina_id': disciplina_id,
        'form': form,
        'errors': errors,
    })



def gerar_pdf_relatorio_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    disciplinas = Disciplina.objects.filter(turma=turma)
    estudantes = Estudante.objects.filter(turma=turma)

    # Montar a tabela de status
    tabela = []
    for estudante in estudantes:
        linha = {
            'estudante': estudante.nome,
            'status_disciplinas': []
        }
        for disciplina in disciplinas:
            nota_final = NotaFinal.objects.filter(estudante=estudante, disciplina=disciplina).first()
            linha['status_disciplinas'].append({
                'disciplina': disciplina.nome,
                'status': nota_final.status if nota_final else 'Sem nota'
            })
        tabela.append(linha)

    # Renderizar o template HTML para PDF
    template_path = 'sistema_notas/relatorio_status_turma_pdf.html'
    context = {'turma': turma, 'disciplinas': disciplinas, 'tabela': tabela}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_turma_{turma.nome}.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    # Gerar o PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Retornar erro se o PDF não puder ser gerado
    if pisa_status.err:
        return HttpResponse('Erro ao gerar o PDF', status=500)
    return response

def relatorio_status_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    disciplinas = Disciplina.objects.filter(turma=turma)
    estudantes = Estudante.objects.filter(turma=turma).prefetch_related('notas__disciplina')

    tabela = []
    for estudante in estudantes:
        linha = {
            'estudante': estudante.nome,
            'status_disciplinas': []
        }
        for disciplina in disciplinas:
            nota_final = estudante.notas.filter(disciplina=disciplina).first()
            linha['status_disciplinas'].append({
                'disciplina': disciplina.nome,
                'status': nota_final.status if nota_final else 'Sem status'
            })
        tabela.append(linha)

    return render(request, 'sistema_notas/relatorio_status_turma.html', {
        'turma': turma,
        'disciplinas': disciplinas,
        'tabela': tabela,
    })