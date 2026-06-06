import numpy as np
import pandas as pd
# Hardcoded maps matching generate_data_and_train.py
CATEGORY_MAP = {'Electronics': 0, 'Grocery': 1, 'Clothing': 2, 'Toys': 3, 'Furniture': 4}
REGION_MAP = {'North': 0, 'South': 1, 'East': 2, 'West': 3}
WEATHER_MAP = {'Sunny': 0, 'Rainy': 1, 'Snowy': 2, 'Cloudy': 3}
SEASON_MAP = {'Spring': 0, 'Summer': 1, 'Autumn': 2, 'Winter': 3}
ECONOMIC_MAP = {'Good': 0, 'Average': 1, 'Poor': 2}
def preprocess_input(data):
    """
    data: dict representing a single row of input
    Returns: a dict of preprocessed numeric values
    """
    preprocessed = {}
    
    # Map categoricals with default values if not found
    preprocessed['category'] = CATEGORY_MAP.get(data.get('category'), 0)
    preprocessed['region'] = REGION_MAP.get(data.get('region'), 0)
    preprocessed['weather_condition'] = WEATHER_MAP.get(data.get('weather_condition'), 0)
    preprocessed['season'] = SEASON_MAP.get(data.get('season'), 0)
    preprocessed['economic_condition'] = ECONOMIC_MAP.get(data.get('economic_condition'), 1) # default average
    # Numericals
    preprocessed['selling_price'] = float(data.get('selling_price', 100.0))
    preprocessed['discount_percentage'] = float(data.get('discount_percentage', 0.0))
    preprocessed['competitor_pricing'] = float(data.get('competitor_pricing', preprocessed['selling_price']))
    preprocessed['promotion_active'] = int(data.get('promotion_active', 0))
    preprocessed['marketing_spend'] = float(data.get('marketing_spend', 0.0))
    preprocessed['units_sold'] = float(data.get('units_sold', 100.0))
    preprocessed['previous_month_sales'] = float(data.get('previous_month_sales', 100.0))
    preprocessed['current_inventory_level'] = float(data.get('current_inventory_level', 100.0))
    preprocessed['units_ordered'] = float(data.get('units_ordered', 0.0))
    preprocessed['safety_stock'] = float(data.get('safety_stock', 50.0))
    preprocessed['lead_time'] = float(data.get('lead_time', 7.0))
    preprocessed['supplier_reliability'] = float(data.get('supplier_reliability', 0.95))
    preprocessed['festival_holiday'] = int(data.get('festival_holiday', 0))
    preprocessed['epidemic_pandemic'] = int(data.get('epidemic_pandemic', 0))
    preprocessed['inflation_rate'] = float(data.get('inflation_rate', 3.0))
    preprocessed['fuel_price_index'] = float(data.get('fuel_price_index', 3.5))
    # Date
    date_val = pd.to_datetime(data.get('date', pd.Timestamp.now()))
    preprocessed['month'] = date_val.month
    preprocessed['quarter'] = date_val.quarter
    preprocessed['weekday'] = date_val.dayofweek
    preprocessed['year'] = date_val.year
    return preprocessed
