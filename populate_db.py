import os
import django
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demand_forecasting_platform.settings')
django.setup()

from forecasting.models import ForecastHistory
from inventory.models import InventoryItem
from alerts.models import Alert
from ai_engine.models import ModelPerformance

def populate():
    print("Applying migrations...")
    from django.core.management import call_command
    call_command('makemigrations')
    call_command('migrate')

    print("Checking and clearing old database records...")
    ForecastHistory.objects.all().delete()
    InventoryItem.objects.all().delete()
    Alert.objects.all().delete()
    ModelPerformance.objects.all().delete()

    print("Seeding Model Performance metrics...")
    ModelPerformance.objects.create(model_name="LightGBM", mae=21.33, rmse=27.10, r2_score=0.9710, is_active=True)
    ModelPerformance.objects.create(model_name="XGBoost", mae=26.20, rmse=33.83, r2_score=0.9548, is_active=False)
    ModelPerformance.objects.create(model_name="Random Forest", mae=36.17, rmse=45.46, r2_score=0.9183, is_active=False)

    print("Seeding Products in Inventory...")
    products_data = [
        {"id": "PRD-1024", "name": "Ultra-Wide Gaming Monitor", "cat": "Electronics", "stock": 45, "ord": 20, "safety": 30, "lt": 5, "rel": 0.98, "wh": "WH-Alpha"},
        {"id": "PRD-4512", "name": "Organic Almond Milk 1L", "cat": "Grocery", "stock": 580, "ord": 150, "safety": 100, "lt": 3, "rel": 0.95, "wh": "WH-Beta"},
        {"id": "PRD-7891", "name": "Denim Slim Fit Jeans", "cat": "Clothing", "stock": 12, "ord": 80, "safety": 40, "lt": 12, "rel": 0.88, "wh": "WH-Gamma"},
        {"id": "PRD-3321", "name": "Wireless Mechanical Keyboard", "cat": "Electronics", "stock": 8, "ord": 50, "safety": 15, "lt": 7, "rel": 0.92, "wh": "WH-Alpha"},
        {"id": "PRD-6543", "name": "Premium Leather Sofa", "cat": "Furniture", "stock": 3, "ord": 2, "safety": 5, "lt": 20, "rel": 0.90, "wh": "WH-Delta"},
        {"id": "PRD-8821", "name": "Educational Building Blocks", "cat": "Toys", "stock": 250, "ord": 0, "safety": 60, "lt": 8, "rel": 0.97, "wh": "WH-Beta"},
        {"id": "PRD-1102", "name": "Noise Cancelling Headphones", "cat": "Electronics", "stock": 85, "ord": 0, "safety": 25, "lt": 6, "rel": 0.96, "wh": "WH-Alpha"},
        {"id": "PRD-4099", "name": "Premium Arabica Coffee Beans 1kg", "cat": "Grocery", "stock": 1400, "ord": 500, "safety": 200, "lt": 4, "rel": 0.99, "wh": "WH-Beta"},
        {"id": "PRD-5050", "name": "Ergonomic Office Chair", "cat": "Furniture", "stock": 28, "ord": 10, "safety": 10, "lt": 15, "rel": 0.85, "wh": "WH-Delta"},
        {"id": "PRD-7732", "name": "Cotton Crewneck T-Shirt", "cat": "Clothing", "stock": 420, "ord": 0, "safety": 80, "lt": 10, "rel": 0.94, "wh": "WH-Gamma"}
    ]

    for p in products_data:
        InventoryItem.objects.create(
            product_id=p["id"],
            product_name=p["name"],
            category=p["cat"],
            current_stock=p["stock"],
            units_ordered=p["ord"],
            safety_stock=p["safety"],
            lead_time=p["lt"],
            supplier_reliability=p["rel"],
            warehouse_location=p["wh"]
        )

    print("Seeding Historical Forecast History...")
    categories = ['Electronics', 'Grocery', 'Clothing', 'Toys', 'Furniture']
    regions = ['North', 'South', 'East', 'West']
    
    # Generate 50 historical entries
    np.random.seed(42)
    start_date = datetime.now() - timedelta(days=60)
    
    for i in range(50):
        prod = products_data[i % len(products_data)]
        forecast_date = start_date + timedelta(days=i)
        
        selling_price = float(np.random.uniform(15.0, 350.0))
        discount = float(np.random.choice([0.0, 5.0, 10.0, 20.0], p=[0.6, 0.2, 0.1, 0.1]))
        promotion = np.random.choice([True, False], p=[0.3, 0.7])
        mkt_spend = float(np.random.uniform(100.0, 500.0) if promotion else 0.0)
        prev_sales = float(np.random.randint(50, 800))
        
        # Calculate a realistic forecasted demand
        base_demand = prev_sales * np.random.uniform(0.9, 1.15)
        if promotion:
            base_demand *= 1.25
        forecasted = int(round(base_demand))
        
        revenue = forecasted * selling_price * (1 - discount/100.0)
        
        # Risk evaluations
        available_stock = prod["stock"] + prod["ord"]
        if available_stock < forecasted:
            stockout = "High"
        elif available_stock < forecasted * 1.3:
            stockout = "Medium"
        else:
            stockout = "Low"
            
        if available_stock > forecasted * 2.5:
            overstock = "High"
        elif available_stock > forecasted * 1.8:
            overstock = "Medium"
        else:
            overstock = "Low"
            
        trend = np.random.choice(["Increasing", "Decreasing", "Stable"], p=[0.4, 0.2, 0.4])
        
        ForecastHistory.objects.create(
            product_id=prod["id"],
            product_name=prod["name"],
            category=prod["cat"],
            region=np.random.choice(regions),
            selling_price=selling_price,
            discount_percentage=discount,
            promotion_active=promotion,
            marketing_spend=mkt_spend,
            previous_month_sales=prev_sales,
            forecasted_demand=forecasted,
            demand_trend=trend,
            confidence_score=float(np.random.uniform(85.0, 98.0)),
            revenue_forecast=float(round(revenue, 2)),
            stockout_risk=stockout,
            overstock_risk=overstock,
            suggested_reorder_quantity=max(0, int(forecasted * 1.2 - available_stock)),
            model_used=np.random.choice(["LightGBM", "XGBoost", "Random Forest"], p=[0.7, 0.2, 0.1]),
            created_at=forecast_date
        )

    print("Seeding Alerts...")
    # Add a critical stockout alert
    Alert.objects.create(
        product_id="PRD-7891",
        product_name="Denim Slim Fit Jeans",
        alert_type="Stockout Risk",
        severity="Critical",
        message="Denim Slim Fit Jeans has high stockout risk. Current inventory (12 units) is far below forecasted monthly demand of 85 units.",
        is_resolved=False
    )
    Alert.objects.create(
        product_id="PRD-3321",
        product_name="Wireless Mechanical Keyboard",
        alert_type="Low Inventory",
        severity="Warning",
        message="Wireless Mechanical Keyboard stock is currently 8 units. Safety stock limit is 15 units. Reorder is recommended.",
        is_resolved=False
    )
    Alert.objects.create(
        product_id="PRD-4099",
        product_name="Premium Arabica Coffee Beans 1kg",
        alert_type="Overstock Warning",
        severity="Warning",
        message="Premium Arabica Coffee Beans 1kg inventory is high (1400 units) compared to forecasted demand of 450 units.",
        is_resolved=False
    )

    print("Database seeding completed successfully.")

if __name__ == "__main__":
    populate()
