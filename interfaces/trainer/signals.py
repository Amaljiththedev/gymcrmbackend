from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.cache import cache

from interfaces.expense.models import Expense
from interfaces.trainer.models import Trainer, TrainerSalaryHistory


@receiver(pre_save, sender=Trainer)
def capture_old_trainer_state(sender, instance, **kwargs):
    """
    Attach old state to the Trainer instance before saving.
    Thread-safe and allows comparison in post_save.
    """
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_state = {
                'salary': old_instance.salary,
                'salary_credited_date': old_instance.salary_credited_date,
                'salary_due_date': old_instance.salary_due_date,
            }
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender=Trainer)
def create_salary_snapshot_and_expense(sender, instance, created, **kwargs):
    """
    After a Trainer is saved, create salary snapshot and log an Expense if needed.
    """
    cache_key = f'salary_snapshot_{instance.pk}'
    cache.delete(cache_key)

    name = instance.name or "Unknown"

    if created:
        # Initial salary snapshot and expense
        TrainerSalaryHistory.objects.create(
            trainer=instance,
            salary=instance.salary,
            salary_credited_date=instance.salary_credited_date,
            salary_due_date=instance.salary_due_date
        )
        try:
            Expense.objects.create(
                title=f"Trainer Salary - {name}",
                amount=instance.salary,
                category="salary",
                description=f"Initial salary payment for {name} (trainer)",
                expense_source="trainer"
            )
        except Exception as e:
            print("❌ Expense creation failed on trainer create:", e)

    else:
        old_state = getattr(instance, '_old_state', None)
        if not old_state:
            return

        salary_changed = old_state['salary'] != instance.salary
        credited_date_changed = old_state['salary_credited_date'] != instance.salary_credited_date

        # Create a new salary history snapshot if salary or credited date changed
        if salary_changed or credited_date_changed:
            TrainerSalaryHistory.objects.create(
                trainer=instance,
                salary=instance.salary,
                salary_credited_date=instance.salary_credited_date,
                salary_due_date=instance.salary_due_date
            )

        # If the credited date changed (i.e., actual salary credit), log as regular salary expense
        if credited_date_changed:
            try:
                Expense.objects.create(
                    title=f"Trainer Salary - {name}",
                    amount=instance.salary,
                    category="salary",
                    description=f"Salary credited for {name} (trainer)",
                    expense_source="trainer"
                )
            except Exception as e:
                print("❌ Expense creation failed on credited date change:", e)


