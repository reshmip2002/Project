# Generated by Django 4.2.10 on 2024-03-03 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sellerapp', '0005_alter_brand_table'),
        ('Userapp', '0006_delete_cart'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCart',
            fields=[
                ('cart_id', models.AutoField(default=None, primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=1, null=True)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Sellerapp.product')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Userapp.user')),
            ],
        ),
    ]
