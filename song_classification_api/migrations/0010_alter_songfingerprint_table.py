# Generated by Django 3.2 on 2021-06-01 21:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('song_classification_api', '0009_alter_songfingerprint_table'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='songfingerprint',
            table='tbl_song_fingerprints',
        ),
    ]