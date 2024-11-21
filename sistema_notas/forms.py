from dal import autocomplete
from django import forms
from .models import NotaFinal, Turma, Disciplina, Estudante
from django.core.exceptions import ValidationError

# Formulário para upload de arquivos CSV
class UploadCSVForm(forms.Form):
    """
    Formulário para permitir o upload de arquivos CSV no sistema.
    """
    arquivo_csv = forms.FileField(label='Selecione o arquivo CSV')  # Campo de upload de arquivo


# Formulário para criar várias disciplinas de uma vez
class DisciplinaMultipleForm(forms.ModelForm):
    """
    Formulário para criar várias disciplinas associadas a turmas.
    """
    nome = forms.CharField(
    widget=forms.TextInput(attrs={
        'placeholder': 'Digite várias disciplinas separadas por vírgula',
        'maxlength': 350,
        'style': 'width: 600px;'  # Ajuste a largura aqui
    }),
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


# Formulário para lançar notas para uma turma e disciplina
class LancaNotaForm(forms.Form):
    """
    Formulário para lançar notas vinculadas a uma turma e disciplina específicas.
    """
    turma = forms.ModelChoiceField(queryset=Turma.objects.all(), label="Turma")
    disciplina = forms.ModelChoiceField(queryset=Disciplina.objects.none(), label="Disciplina")

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário e ajusta o queryset de disciplinas baseado na turma.
        """
        super().__init__(*args, **kwargs)
        if 'turma' in self.data:
            try:
                turma_id = int(self.data.get('turma'))
                self.fields['disciplina'].queryset = Disciplina.objects.filter(turma_id=turma_id)
            except (ValueError, TypeError):
                self.fields['disciplina'].queryset = Disciplina.objects.none()


# Formulário para adicionar ou editar uma nota final
class NotaFinalForm(forms.ModelForm):
    """
    Formulário para registrar notas finais vinculadas a estudantes, turmas e disciplinas.
    """
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
        """
        Inicializa o formulário, ajustando os querysets com base na seleção de turma e disciplina.
        """
        super().__init__(*args, **kwargs)

        # Carregar disciplinas com base na turma
        if 'turma' in self.data:
            try:
                turma_id = int(self.data.get('turma'))
                self.fields['disciplina'].queryset = Disciplina.objects.filter(turma_id=turma_id)
            except (ValueError, TypeError):
                self.fields['disciplina'].queryset = Disciplina.objects.none()

        # Carregar estudantes com base na disciplina e turma
        if 'disciplina' in self.data:
            try:
                disciplina_id = int(self.data.get('disciplina'))
                turma_id = int(self.data.get('turma'))
                self.fields['estudante'].queryset = Estudante.objects.filter(
                    turma_id=turma_id,
                    turma__disciplinas__id=disciplina_id
                )
            except (ValueError, TypeError):
                self.fields['estudante'].queryset = Estudante.objects.none()

    def clean(self):
        """
        Valida os dados do formulário para evitar duplicatas de notas finais.
        """
        cleaned_data = super().clean()
        estudante = cleaned_data.get('estudante')
        disciplina = cleaned_data.get('disciplina')

        # Verificar duplicatas
        if NotaFinal.objects.filter(estudante=estudante, disciplina=disciplina).exists():
            raise ValidationError("Já existe uma nota cadastrada para este estudante nesta disciplina.")

        return cleaned_data


# Formulário para lançar notas em massa por turma
class LancarNotasForm(forms.Form):
    """
    Formulário simplificado para lançar notas em massa para uma turma e disciplina.
    """
    turma = forms.ModelChoiceField(queryset=Turma.objects.all(), label="Turma")
    disciplina = forms.ModelChoiceField(queryset=Disciplina.objects.none(), label="Disciplina")

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário e ajusta o queryset de disciplinas baseado na turma.
        """
        super().__init__(*args, **kwargs)
        if 'turma' in self.data:
            try:
                turma_id = int(self.data.get('turma'))
                self.fields['disciplina'].queryset = Disciplina.objects.filter(turma_id=turma_id)
            except (ValueError, TypeError):
                pass
