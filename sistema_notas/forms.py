from django import forms
from .models import Disciplina, Turma
from django.contrib import messages
from django.shortcuts import redirect

class UploadCSVForm(forms.Form):
    arquivo_csv = forms.FileField(label='Selecione o arquivo CSV')

class DisciplinaMultipleForm(forms.ModelForm):
    nome = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Digite várias disciplinas separadas por vírgula'}),
        help_text="Exemplo: Matemática, Física, Química"
    )
    turmas = forms.ModelMultipleChoiceField(
        queryset=Turma.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Selecione as turmas para associar cada disciplina."
    )

    class Meta:
        model = Disciplina
        fields = ['nome', 'turmas']