# Generated by Django 4.0.1 on 2022-01-07 22:40

from django.db import migrations
import oauth2_provider.generators
import oauth2_provider.models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2_provider', '0005_auto_20211222_2352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='client_secret',
            field=oauth2_provider.models.ClientSecretField(blank=True, db_index=True, default=oauth2_provider.generators.generate_client_secret, max_length=255),
        ),
    ]