from django.db import models
class Alert(models.Model):
    ALERT_TYPES = [
        ('Low Inventory', 'Low Inventory'),
        ('Stockout Risk', 'Stockout Risk'),
        ('Overstock Warning', 'Overstock Warning'),
        ('Abnormal Demand', 'Abnormal Demand'),
    ]
    SEVERITY_LEVELS = [
        ('Critical', 'Critical'),
        ('Warning', 'Warning'),
        ('Info', 'Info'),
    ]
    product_id = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"[{self.severity}] {self.alert_type} for {self.product_name}"