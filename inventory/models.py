from django.db import models
class InventoryItem(models.Model):
    product_id = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    current_stock = models.IntegerField()
    units_ordered = models.IntegerField(default=0)
    safety_stock = models.IntegerField(default=50)
    lead_time = models.IntegerField(default=7) # in days
    supplier_reliability = models.FloatField(default=0.95)
    warehouse_location = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.product_name} ({self.current_stock} units)"
