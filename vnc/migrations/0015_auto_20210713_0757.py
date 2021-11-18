# Generated by Django 3.2.4 on 2021-07-13 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vnc', '0014_alter_empresa_nro_wpp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compromiso',
            name='id_empresa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vnc.empresa'),
        ),
        migrations.AlterField(
            model_name='compromiso',
            name='localidad',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vnc.localidad'),
        ),
        migrations.AlterField(
            model_name='compromiso',
            name='provincia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vnc.provincia'),
        ),
        migrations.AlterField(
            model_name='usuarioempresa',
            name='empresa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vnc.empresa'),
        ),
    ]