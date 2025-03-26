# Generated by Django 5.1.6 on 2025-03-25 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_paymenthistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymenthistory',
            name='remaining_balance',
        ),
        migrations.RemoveField(
            model_name='paymenthistory',
            name='total_paid',
        ),
        migrations.AddField(
            model_name='member',
            name='remaining_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, editable=False, help_text='Remaining balance for the current cycle', max_digits=10),
        ),
        migrations.AddField(
            model_name='member',
            name='renewal_count',
            field=models.PositiveIntegerField(default=0, help_text='Renewal cycle count'),
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='renewal_count',
            field=models.PositiveIntegerField(default=0, help_text='Renewal cycle for this transaction'),
        ),
        migrations.AlterField(
            model_name='member',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Amount paid for the current membership cycle', max_digits=10),
        ),
    ]
