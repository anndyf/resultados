import csv
from django.shortcuts import render, redirect
from .models import Estudante, Turma
from .forms import UploadCSVForm
from django.contrib import messages

def listar_status_turma(request, turma_id):
    turma = Turma.objects.get(id=turma_id)
    estudantes = turma.estudantes.all()
    return render(request, 'sistema_notas/listar_status_turma.html', {'turma': turma, 'estudantes': estudantes})

def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['arquivo_csv']
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                next(reader)  # Ignora o cabeçalho do CSV
                for row in reader:
                    nome_estudante = row[0]
                    turma_nome = row[1]
                    # Verifica se a turma já existe; caso contrário, cria uma nova
                    turma, created = Turma.objects.get_or_create(nome=turma_nome)
                    # Cadastra o estudante associado à turma
                    Estudante.objects.create(nome=nome_estudante, turma=turma)
                messages.success(request, "Estudantes cadastrados com sucesso!")
            except Exception as e:
                messages.error(request, f"Erro ao processar o arquivo: {e}")
            return redirect('upload_csv')
    else:
        form = UploadCSVForm()
    return render(request, 'sistema_notas/upload_csv.html', {'form': form})