# Generated by Django 5.1.6 on 2025-03-23 16:42

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('duration_days', models.PositiveIntegerField(help_text='Duration of the plan in days')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_blocked', models.BooleanField(default=False, help_text='If blocked, the plan cannot be assigned to new members.')),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10, null=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, help_text='Height in cm', max_digits=5, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, help_text='Weight in kg', max_digits=5, null=True)),
                ('dob', models.DateField(blank=True, help_text='Date of Birth', null=True)),
                ('age', models.PositiveIntegerField(blank=True, help_text='Age in years', null=True)),
                ('membership_start', models.DateTimeField(help_text='Manually set by the manager')),
                ('membership_end', models.DateTimeField(blank=True, help_text='Computed membership end datetime', null=True)),
                ('is_blocked', models.BooleanField(default=False, help_text='Mark if member is blocked')),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0.0, help_text='Amount paid so far', max_digits=10)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='member_photos/')),
                ('membership_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='members.membershipplan')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance_date', models.DateField(default=django.utils.timezone.now)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='members.member')),
            ],
            options={
                'ordering': ['-attendance_date'],
                'indexes': [models.Index(fields=['member'], name='members_att_member__19867c_idx'), models.Index(fields=['attendance_date'], name='members_att_attenda_ca94c1_idx')],
                'unique_together': {('member', 'attendance_date')},
            },
        ),
        migrations.AddIndex(
            model_name='member',
            index=models.Index(fields=['membership_start'], name='members_mem_members_eef670_idx'),
        ),
        migrations.AddIndex(
            model_name='member',
            index=models.Index(fields=['membership_end'], name='members_mem_members_3e76ae_idx'),
        ),
        migrations.AddIndex(
            model_name='member',
            index=models.Index(fields=['dob'], name='members_mem_dob_282b1f_idx'),
        ),
    ]
