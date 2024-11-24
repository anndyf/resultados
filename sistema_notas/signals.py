from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import NotaFinal, NotaFinalAudit


@receiver(pre_save, sender=NotaFinal)
def registrar_historico(sender, instance, **kwargs):
    """
    Cria um registro de auditoria antes de salvar uma NotaFinal.
    Garante que as duplicações sejam evitadas.
    """
    if instance.pk:  # Verifica se é uma atualização (instância já existe no banco)
        nota_original = NotaFinal.objects.filter(pk=instance.pk).first()
        if nota_original and nota_original.nota != instance.nota:  # Somente se a nota foi alterada
            # Verifica se já existe um registro para essa alteração
            existe_auditoria = NotaFinalAudit.objects.filter(
                nota_final=instance,
                nota_anterior=nota_original.nota,
                nota_atual=instance.nota,
                modified_by=instance.modified_by,
            ).exists()

            if not existe_auditoria:
                NotaFinalAudit.objects.create(
                    nota_final=instance,
                    modified_by=instance.modified_by,  # Usuário que fez a alteração
                    nota_anterior=nota_original.nota,
                    nota_atual=instance.nota,
                    status=instance.status,  # Inclui o status no registro
                )