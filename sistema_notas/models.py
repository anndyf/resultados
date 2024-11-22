from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError

# Obtém o modelo de usuário do Django
User = get_user_model()

# Modelo para representar uma Turma
class Turma(models.Model):
    """
    Representa uma turma no sistema, que pode ter vários estudantes e disciplinas associadas.
    """
    nome = models.CharField(max_length=100)  # Nome da turma

    def __str__(self):
        return self.nome

# Modelo para representar um Estudante
class Estudante(models.Model):
    """
    Representa um estudante associado a uma turma específica.
    """
    nome = models.CharField(max_length=100)  # Nome do estudante
    turma = models.ForeignKey(
        Turma, 
        on_delete=models.CASCADE, 
        related_name='estudantes'
    )  # Relaciona o estudante a uma turma

    def __str__(self):
        return self.nome

# Modelo para representar uma Disciplina
class Disciplina(models.Model):
    """
    Representa uma disciplina associada a uma turma específica.
    """
    nome = models.CharField(max_length=300)  # Nome da disciplina
    turma = models.ForeignKey(
        Turma, 
        on_delete=models.CASCADE, 
        related_name='disciplinas'
    )  # Relaciona a disciplina a uma turma

    def __str__(self):
        # Exibe o nome da disciplina junto com o nome da turma
        return f"{self.nome} - {self.turma.nome}"

# Modelo para representar o relacionamento entre uma Disciplina e uma Turma
class DisciplinaTurma(models.Model):
    """
    Representa a relação entre uma disciplina e uma turma em um ano letivo específico.
    """
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)  # Disciplina associada
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)  # Turma associada
    ano_letivo = models.CharField(max_length=10, blank=True, null=True)  # Ano letivo da disciplina

    def __str__(self):
        # Exibe a relação entre disciplina, turma e ano letivo
        return f"{self.disciplina.nome} - {self.turma.nome} ({self.ano_letivo})"

# Modelo para representar uma Nota Final
class NotaFinal(models.Model):
    """
    Representa a nota final de um estudante em uma disciplina.
    """
    estudante = models.ForeignKey(
        'Estudante', 
        on_delete=models.CASCADE, 
        related_name='notas'
    )
    disciplina = models.ForeignKey(
        'Disciplina', 
        on_delete=models.CASCADE, 
        related_name='notas'
    )
    nota = models.FloatField()
    STATUS_CHOICES = [
        ('Aprovado', 'Aprovado'),
        ('Recuperação', 'Recuperação'),
        ('Desistente', 'Desistente'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        blank=True
    )

    class Meta:
        unique_together = ('estudante', 'disciplina')
        verbose_name = 'Nota Final'
        verbose_name_plural = 'Notas Finais'

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para calcular automaticamente o status com base na nota.
        """
        # Recalcula o status com base no valor da nota
        if self.nota == -1:
            self.status = 'Desistente'
        elif self.nota < 5:
            self.status = 'Recuperação'
        else:
            self.status = 'Aprovado'

        # Chama o método save da superclasse para persistir os dados
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.estudante.nome} - {self.disciplina.nome}: {self.nota} ({self.status})"
