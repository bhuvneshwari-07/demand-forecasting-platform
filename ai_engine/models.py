from django.db import models
class ModelPerformance(models.Model):
    model_name = models.CharField(max_length=50) # Random Forest, XGBoost, LightGBM
    mae = models.FloatField()
    rmse = models.FloatField()
    r2_score = models.FloatField()
    trained_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.model_name} (R2={self.r2_score:.4f})"