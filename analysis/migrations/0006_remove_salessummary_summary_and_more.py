# Generated by Django 5.0 on 2024-08-24 03:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0005_remove_salessummary_summary_trends'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salessummary',
            name='summary',
        ),
        migrations.RemoveField(
            model_name='salessummary',
            name='summary_month',
        ),
        migrations.RemoveField(
            model_name='salessummary',
            name='summary_products',
        ),
        migrations.RemoveField(
            model_name='salessummary',
            name='summary_sales',
        ),
        migrations.RemoveField(
            model_name='salessummary',
            name='top_month_sales',
        ),
    ]
