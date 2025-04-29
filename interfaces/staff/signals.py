from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Staff, StaffSalaryHistory
from interfaces.expense.models import Expense


@receiver(pre_save, sender=Staff)
def capture_old_staff_state(sender, instance, **kwargs):
    """
    Capture the old state of the Staff instance before saving.
    This avoids using global state and works safely across threads.
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


@receiver(post_save, sender=Staff)
def create_salary_snapshot_and_expense(sender, instance, created, **kwargs):
    """
    Creates a salary history snapshot and logs it as an expense when staff salary is updated or added.
    """
    cache_key = f'salary_snapshot_{instance.pk}'
    cache.delete(cache_key)

    full_name = f"{instance.first_name} {instance.last_name}".strip() or "Unnamed"
    department = getattr(instance, "department", "General")

    if created:
        # Initial snapshot and expense
        StaffSalaryHistory.objects.create(
            staff=instance,
            salary=instance.salary,
            salary_credited_date=instance.salary_credited_date,
            salary_due_date=instance.salary_due_date
        )

        try:
            Expense.objects.create(
                title=f"Staff Salary - {full_name}",
                amount=instance.salary,
                category="salary",
                description=f"Initial salary payment for {full_name} ({department})",
                expense_source="staff"
            )
        except Exception as e:
            print("❌ Expense creation failed on staff create:", e)

    else:
        old_state = getattr(instance, '_old_state', None)
        if not old_state:
            return

        salary_changed = old_state['salary'] != instance.salary
        credited_date_changed = old_state['salary_credited_date'] != instance.salary_credited_date

        if credited_date_changed:
            StaffSalaryHistory.objects.create(
                staff=instance,
                salary=instance.salary,
                salary_credited_date=instance.salary_credited_date,
                salary_due_date=instance.salary_due_date
            )

            try:
                Expense.objects.create(
                    title=f"Staff Salary - {full_name}",
                    amount=instance.salary,
                    category="salary",
                    description=f"Salary payment for {full_name} ({department})",
                    expense_source="staff"
                )
            except Exception as e:
                print("❌ Expense creation failed on credited date change:", e)

