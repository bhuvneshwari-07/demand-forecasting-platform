import os
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
# Create directories
os.makedirs('static/datasets', exist_ok=True)
os.makedirs('trained_models', exist_ok=True)
# Generate synthetic dataset
print("Generating synthetic dataset...")
np.random.seed(42)
n_samples = 2000
# Features
dates = pd.date_range(start='2024-01-01', periods=n_samples, freq='D')
product_ids = [f"PRD-{np.random.randint(1000, 9999)}" for _ in range(n_samples)]
product_names = [f"Product {pid.split('-')[1]}" for pid in product_ids]
categories = np.random.choice(['Electronics', 'Grocery', 'Clothing', 'Toys', 'Furniture'], size=n_samples)
regions = np.random.choice(['North', 'South', 'East', 'West'], size=n_samples)
warehouse_locations = np.random.choice(['WH-Alpha', 'WH-Beta', 'WH-Gamma', 'WH-Delta'], size=n_samples)
selling_prices = np.random.uniform(10.0, 500.0, size=n_samples)
discount_percentages = np.random.uniform(0.0, 50.0, size=n_samples)
competitor_pricings = selling_prices * np.random.uniform(0.9, 1.1, size=n_samples)
promotions_active = np.random.choice([0, 1], p=[0.7, 0.3], size=n_samples)
marketing_spends = promotions_active * np.random.uniform(50.0, 1000.0, size=n_samples) + np.random.uniform(0.0, 50.0, size=n_samples)
units_sold_current = np.random.randint(10, 1000, size=n_samples)
prev_month_sales = units_sold_current * np.random.uniform(0.8, 1.2, size=n_samples)
current_inventory_levels = np.random.randint(50, 2000, size=n_samples)
units_ordered = np.random.randint(0, 500, size=n_samples)
safety_stocks = np.random.randint(20, 200, size=n_samples)
lead_times = np.random.randint(2, 20, size=n_samples)
supplier_reliabilities = np.random.uniform(0.7, 1.0, size=n_samples)
weather_conditions = np.random.choice(['Sunny', 'Rainy', 'Snowy', 'Cloudy'], size=n_samples)
seasons = np.random.choice(['Spring', 'Summer', 'Autumn', 'Winter'], size=n_samples)
festivals_holidays = np.random.choice([0, 1], p=[0.85, 0.15], size=n_samples)
epidemic_pandemics = np.zeros(n_samples) # baseline 0
inflation_rates = np.random.uniform(1.5, 6.0, size=n_samples)
fuel_price_indices = np.random.uniform(2.5, 4.5, size=n_samples)
economic_conditions = np.random.choice(['Good', 'Average', 'Poor'], p=[0.4, 0.5, 0.1], size=n_samples)
# Derive date components
months = dates.month
quarters = dates.quarter
weekdays = dates.dayofweek
years = dates.year
# Create DataFrame
df = pd.DataFrame({
    'date': dates,
    'product_id': product_ids,
    'product_name': product_names,
    'category': categories,
    'region': regions,
    'warehouse_location': warehouse_locations,
    'selling_price': selling_prices,
    'discount_percentage': discount_percentages,
    'competitor_pricing': competitor_pricings,
    'promotion_active': promotions_active,
    'marketing_spend': marketing_spends,
    'units_sold': units_sold_current,
    'previous_month_sales': prev_month_sales,
    'current_inventory_level': current_inventory_levels,
    'units_ordered': units_ordered,
    'safety_stock': safety_stocks,
    'lead_time': lead_times,
    'supplier_reliability': supplier_reliabilities,
    'weather_condition': weather_conditions,
    'season': seasons,
    'festival_holiday': festivals_holidays,
    'epidemic_pandemic': epidemic_pandemics,
    'inflation_rate': inflation_rates,
    'fuel_price_index': fuel_price_indices,
    'economic_condition': economic_conditions,
    'month': months,
    'quarter': quarters,
    'weekday': weekdays,
    'year': years
})
# Calculate realistic target variable (forecasted_demand)
base_demand = 50.0
category_effects = {'Electronics': 120.0, 'Grocery': 80.0, 'Clothing': 60.0, 'Toys': 40.0, 'Furniture': 30.0}
region_effects = {'North': 10.0, 'South': 5.0, 'East': 15.0, 'West': 20.0}
weather_effects = {'Sunny': 15.0, 'Rainy': -10.0, 'Snowy': -25.0, 'Cloudy': 5.0}
season_effects = {'Spring': 10.0, 'Summer': 25.0, 'Autumn': 5.0, 'Winter': -15.0}
economic_effects = {'Good': 30.0, 'Average': 10.0, 'Poor': -40.0}
df['forecasted_demand'] = (
    base_demand
    + df['category'].map(category_effects)
    + df['region'].map(region_effects)
    + df['weather_condition'].map(weather_effects)
    + df['season'].map(season_effects)
    + df['economic_condition'].map(economic_effects)
    - (df['selling_price'] * 0.1)
    + (df['discount_percentage'] * 2.5)
    + (df['promotion_active'] * 50.0)
    + (df['marketing_spend'] * 0.08)
    + (df['previous_month_sales'] * 0.45)
    + (df['festival_holiday'] * 60.0)
    + np.random.normal(0, 15, n_samples) # noise
)
# Clip demand to be positive and convert to int
df['forecasted_demand'] = df['forecasted_demand'].clip(lower=5).round().astype(int)
# Save synthetic dataset to static/datasets/
df.to_csv('static/datasets/retail_historical_sales.csv', index=False)
print("Synthetic dataset saved successfully to static/datasets/retail_historical_sales.csv")
# Categorical mappings
category_map = {'Electronics': 0, 'Grocery': 1, 'Clothing': 2, 'Toys': 3, 'Furniture': 4}
region_map = {'North': 0, 'South': 1, 'East': 2, 'West': 3}
weather_map = {'Sunny': 0, 'Rainy': 1, 'Snowy': 2, 'Cloudy': 3}
season_map = {'Spring': 0, 'Summer': 1, 'Autumn': 2, 'Winter': 3}
economic_map = {'Good': 0, 'Average': 1, 'Poor': 2}
# Preprocess DataFrame for ML model training
X = df.copy()
X['category'] = X['category'].map(category_map)
X['region'] = X['region'].map(region_map)
X['weather_condition'] = X['weather_condition'].map(weather_map)
X['season'] = X['season'].map(season_map)
X['economic_condition'] = X['economic_condition'].map(economic_map)
# Select numerical features for training
features = [
    'category', 'region', 'selling_price', 'discount_percentage', 'competitor_pricing',
    'promotion_active', 'marketing_spend', 'units_sold', 'previous_month_sales',
    'current_inventory_level', 'units_ordered', 'safety_stock', 'lead_time',
    'supplier_reliability', 'weather_condition', 'season', 'festival_holiday',
    'epidemic_pandemic', 'inflation_rate', 'fuel_price_index', 'economic_condition',
    'month', 'quarter', 'weekday', 'year'
]
y = X['forecasted_demand']
X_features = X[features]
X_train, X_test, y_train, y_test = train_test_split(X_features, y, test_size=0.2, random_state=42)
# Random Forest
print("Training Random Forest...")
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
print(f"Random Forest MAE: {mean_absolute_error(y_test, rf_pred):.2f}, RMSE: {root_mean_squared_error(y_test, rf_pred):.2f}, R2: {r2_score(y_test, rf_pred):.4f}")
joblib.dump(rf, 'trained_models/random_forest.pkl')
# XGBoost
print("Training XGBoost...")
xgb = XGBRegressor(n_estimators=100, random_state=42)
xgb.fit(X_train, y_train)
xgb_pred = xgb.predict(X_test)
print(f"XGBoost MAE: {mean_absolute_error(y_test, xgb_pred):.2f}, RMSE: {root_mean_squared_error(y_test, xgb_pred):.2f}, R2: {r2_score(y_test, xgb_pred):.4f}")
joblib.dump(xgb, 'trained_models/xgboost.pkl')
# LightGBM
print("Training LightGBM...")
lgb = LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)
lgb.fit(X_train, y_train)
lgb_pred = lgb.predict(X_test)
print(f"LightGBM MAE: {mean_absolute_error(y_test, lgb_pred):.2f}, RMSE: {root_mean_squared_error(y_test, lgb_pred):.2f}, R2: {r2_score(y_test, lgb_pred):.4f}")
joblib.dump(lgb, 'trained_models/lightgbm.pkl')
print("All models trained and saved to trained_models/")
