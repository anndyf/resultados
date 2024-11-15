from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError

User = get_user_model()

class Turma(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Estudante(models.Model):
    nome = models.CharField(max_length=100)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='estudantes')

    def __str__(self):
        return self.nome

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='disciplinas')  # Relacionamento um para muitos

    def __str__(self):
        return f"{self.nome} - {self.turma.nome}"  # Mostra a disciplina com o nome da turma para evitar duplicação

class DisciplinaTurma(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    ano_letivo = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.disciplina.nome} - {self.turma.nome} ({self.ano_letivo})"
    
class NotaFinal(models.Model):
    estudante = models.ForeignKey('Estudante', on_delete=models.CASCADE, related_name='notas')
    disciplina = models.ForeignKey('Disciplina', on_delete=models.CASCADE, related_name='notas')
    nota = models.FloatField()
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE)  # Certifique-se disso
    STATUS_CHOICES = [
        ('Aprovado', 'Aprovado'),
        ('Recuperação', 'Recuperação'),
        ('Desistente', 'Desistente'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='notas_registradas')

    class Meta:
        unique_together = ('estudante', 'disciplina')
        verbose_name = 'Nota Final'
        verbose_name_plural = 'Notas Finais'

    def save(self, *args, **kwargs):
        # Verificar se a nota já existe para o estudante e disciplina antes de salvar
        if NotaFinal.objects.filter(estudante=self.estudante, disciplina=self.disciplina).exists():
            raise ValidationError("Já existe uma nota para esse estudante nessa disciplina.")

        # Define o status automaticamente com base na nota
        if self.nota == -1:
            self.status = 'Desistente'
        elif self.nota < 5:
            self.status = 'Recuperação'
        else:
            self.status = 'Aprovado'
        
        # Define o usuário que registrou, se ainda não estiver definido
        if not self.registrado_por and kwargs.get('user'):
            self.registrado_por = kwargs.pop('user')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.estudante.nome} - {self.disciplina.nome}: {self.nota} ({self.status})"