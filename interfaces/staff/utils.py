from django.core.cache import cache
from .models import StaffSalaryHistory

def get_staff_salary_history(staff_id, timeout=300):
    cache_key = f'staff_salary_history_{staff_id}'
    history = cache.get(cache_key)
    if history is None:
        history = list(
            StaffSalaryHistory.objects.filter(staff_id=staff_id)
            .order_by('-paid_on')
            .values(
                'id',
                'staff_id',
                'amount',
                'paid_on',
                'due_date',
                'expense_record_id'
            )
        )
        cache.set(cache_key, history, timeout)
    return history
