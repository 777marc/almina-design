from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_order_payment_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_carrier',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_service',
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
