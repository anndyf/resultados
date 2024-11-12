from django import forms
from .models import Disciplina, Turma
from django.contrib import messages
from django.shortcuts import redirect
from .models import NotaFinal, Turma, Disciplina, Estudante
from dal import autocomplete

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

class LancaNotaForm(forms.Form):
    turma = forms.ModelChoiceField(queryset=Turma.objects.all(), label="Turma")
    disciplina = forms.ModelChoiceField(queryset=Disciplina.objects.none(), label="Disciplina")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'turma' in self.data:
            try:
                turma_id = int(self.data.get('turma'))
                self.fields['disciplina'].queryset = Disciplina.objects.filter(turma_id=turma_id)
            except (ValueError, TypeError):
                pass


class NotaFinalForm(forms.ModelForm):
    turma = forms.ModelChoiceField(queryset=Turma.objects.all(), required=True, label="Turma")
    disciplina = forms.ModelChoiceField(
        queryset=Disciplina.objects.none(),
        required=True,
        label="Disciplina",
        widget=autocomplete.ModelSelect2(url='disciplina-autocomplete', forward=['turma'])
    )
    estudante = forms.ModelChoiceField(
        queryset=Estudante.objects.none(),
        required=True,
        label="Estudante",
        widget=autocomplete.ModelSelect2(url='estudante-autocomplete', forward=['turma', 'disciplina'])  # Envia os valores de "Turma" e "Disciplina"
    )

    class Meta:
        model = NotaFinal
        fields = ['turma', 'disciplina', 'estudante', 'nota', 'status']  # Ordem dos campos ajustada

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'turma' in self.data:
            try:
                turma_id = int(self.data.get('turma'))
                self.fields['disciplina'].queryset = Disciplina.objects.filter(turma__id=turma_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['disciplina'].queryset = self.instance.turma.disciplinas_set

class LancaNotaPorDisciplinaForm(forms.Form):
    disciplina = forms.ModelChoiceField(queryset=Disciplina.objects.all(), required=True, label="Disciplina")
    
    class Meta:
        fields = ['disciplina']