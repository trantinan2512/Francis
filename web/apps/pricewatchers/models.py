from django.db import models


class TikiProduct(models.Model):
    page_id = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=2000, blank=True)
    current_lowest_price = models.BigIntegerField(default=1000000000)
    lowest_price = models.BigIntegerField(default=1000000000)
    out_of_stock = models.BooleanField(default=False)
    error = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.page_id
