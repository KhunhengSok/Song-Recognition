# Generated by Django 3.2 on 2021-05-18 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('song_classification_api', '0005_song_album'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='id',
            field=models.AutoField(db_index=True, editable=False, primary_key=True, serialize=False),
        ),
    ]