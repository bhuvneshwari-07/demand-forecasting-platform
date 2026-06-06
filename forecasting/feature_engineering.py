import pandas as pd
FEATURES = [
    'category', 'region', 'selling_price', 'discount_percentage', 'competitor_pricing',
    'promotion_active', 'marketing_spend', 'units_sold', 'previous_month_sales',
    'current_inventory_level', 'units_ordered', 'safety_stock', 'lead_time',
    'supplier_reliability', 'weather_condition', 'season', 'festival_holiday',
    'epidemic_pandemic', 'inflation_rate', 'fuel_price_index', 'economic_condition',
    'month', 'quarter', 'weekday', 'year'
]
def format_features(preprocessed_dict):
    """
    Takes a preprocessed single row dictionary and returns a pandas DataFrame with features in correct order.
    """
    df = pd.DataFrame([preprocessed_dict])
    return df[FEATURES]