from .models import NotaFinal, NotaFinalAudit
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=NotaFinal)
def registrar_historico(sender, instance, **kwargs):
    """
    Registra uma auditoria no modelo NotaFinalAudit sempre que uma nota for alterada.
    """
    if instance.pk:  # Verifica se a instância já existe no banco
        try:
            nota_original = NotaFinal.objects.get(pk=instance.pk)
            if nota_original.nota != instance.nota:  # Verifica se a nota foi alterada
                NotaFinalAudit.objects.create(
                    nota_final=instance,
                    modified_by=instance.modified_by,  # Certifica-se de que `modified_by` seja atribuído antes de salvar
                    nota_anterior=nota_original.nota,
                    nota_atual=instance.nota,
                )
        except NotaFinal.DoesNotExist:
            # Caso a nota original não exista, não faz nada
            pass
