# interfaces/expense/tasks.py

from celery import shared_task

@shared_task
def test_expense_log(x, y):
    print("📦 Running task inside Celery!")
    return x + y