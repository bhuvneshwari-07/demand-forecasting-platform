from django.db import models
class ForecastHistory(models.Model):
    product_id = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    selling_price = models.FloatField()
    discount_percentage = models.FloatField()
    promotion_active = models.BooleanField(default=False)
    marketing_spend = models.FloatField(default=0.0)
    previous_month_sales = models.FloatField(default=0.0)
    forecasted_demand = models.IntegerField()
    demand_trend = models.CharField(max_length=20, default="Stable")
    confidence_score = models.FloatField(default=0.0)
    revenue_forecast = models.FloatField(default=0.0)
    stockout_risk = models.CharField(max_length=20, default="Low")
    overstock_risk = models.CharField(max_length=20, default="Low")
    suggested_reorder_quantity = models.IntegerField(default=0)
    model_used = models.CharField(max_length=50, default="LightGBM")
    
    # External Factors & Date parameters
    weather_condition = models.CharField(max_length=50, default="Sunny")
    season = models.CharField(max_length=50, default="Summer")
    festival_holiday = models.BooleanField(default=False)
    epidemic_pandemic = models.BooleanField(default=False)
    inflation_rate = models.FloatField(default=3.0)
    fuel_price_index = models.FloatField(default=3.5)
    economic_condition = models.CharField(max_length=50, default="Average")
    
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.product_name} - {self.forecasted_demand} ({self.created_at.strftime('%Y-%m-%d')})"