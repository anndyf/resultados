from dal import autocomplete
from django import forms
from .models import Disciplina, Turma
from django.contrib import messages
from django.shortcuts import redirect
from .models import NotaFinal, Turma, Disciplina, Estudante
from dal import autocomplete
from django.core.exceptions import ValidationError

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
    turma = forms.ModelChoiceField(
        queryset=Turma.objects.all(),
        required=True,
        label="Turma"
    )
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
        widget=autocomplete.ModelSelect2(url='estudante-autocomplete', forward=['turma', 'disciplina'])
    )
    nota = forms.FloatField(
        label="Nota",
        help_text="Digite -1 para classificar como desistente"
    )

    class Meta:
        model = NotaFinal
        fields = ['turma', 'disciplina', 'estudante', 'nota']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Carregar disciplinas com base na turma
        if 'turma' in self.data:
            try:
                turma_id = int(self.data.get('turma'))
                self.fields['disciplina'].queryset = Disciplina.objects.filter(turma_id=turma_id)
            except (ValueError, TypeError):
                self.fields['disciplina'].queryset = Disciplina.objects.none()

        # Carregar estudantes com base na disciplina
        if 'disciplina' in self.data:
            try:
                disciplina_id = int(self.data.get('disciplina'))
                self.fields['estudante'].queryset = Estudante.objects.filter(turma_id=self.data.get('turma'))
            except (ValueError, TypeError):
                self.fields['estudante'].queryset = Estudante.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        estudante = cleaned_data.get('estudante')
        disciplina = cleaned_data.get('disciplina')

        # Verificar duplicatas
        if NotaFinal.objects.filter(estudante=estudante, disciplina=disciplina).exists():
            raise ValidationError("Já existe uma nota cadastrada para este estudante nesta disciplina.")

        return cleaned_data
    
class LancarNotasForm(forms.Form):
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