# Generated by Django 3.2.18 on 2023-04-06 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_auto_20230405_2203'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imageshow',
            old_name='post',
            new_name='posts',
        ),
        migrations.AddField(
            model_name='post',
            name='image_slide',
            field=models.ManyToManyField(to='backend.imageShow'),
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.TextField(
                blank=True, max_length=100, null=True, verbose_name='Tags'),
        ),
    ]
