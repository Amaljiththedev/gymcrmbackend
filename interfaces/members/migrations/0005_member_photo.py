# Generated by Django 5.1.6 on 2025-03-04 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_member_amount_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='member_photos/'),
        ),
    ]
