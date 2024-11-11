from django.db import models

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
    estudante = models.ForeignKey(Estudante, on_delete=models.CASCADE, related_name='notas')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='notas')
    nota = models.FloatField()
    STATUS_CHOICES = [
        ('Aprovado', 'Aprovado'),
        ('Recuperação', 'Recuperação'),
        ('Desistente', 'Desistente'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.estudante.nome} - {self.disciplina.nome}: {self.nota} ({self.status})"
