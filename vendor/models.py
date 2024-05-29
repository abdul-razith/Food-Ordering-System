from django.db import models

# Create your models here.

class OrdersRecords(models.Model):
    order_id = models.IntegerField()
    user_id = models.IntegerField()
    user_name = models.CharField(max_length = 30)
    cart_items = models.JSONField()
    total = models.IntegerField(null=True)
    order_at = models.DateTimeField()

    def __str__(self):
        return self.user_name