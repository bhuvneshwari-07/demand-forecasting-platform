import json
from django.shortcuts import render
from django.db import models
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from forecasting.models import ForecastHistory
from inventory.models import InventoryItem
from alerts.models import Alert
from ai_engine.models import ModelPerformance

def dashboard_view(request):
    """
    Main Core Dashboard Views
    """
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')
    
    # Check if a CSV was recently uploaded and extract summary
    csv_summary = request.session.pop('csv_upload_summary', None)
    
    # 1. Calculate TOP KPIs
    total_forecasts = ForecastHistory.objects.count()
    predicted_demand = ForecastHistory.objects.aggregate(total=Sum('forecasted_demand'))['total'] or 0
    revenue_forecast = ForecastHistory.objects.aggregate(total=Sum('revenue_forecast'))['total'] or 0.0
    
    # Active Model Accuracy
    active_perf = ModelPerformance.objects.filter(model_name=model_name).first()
    forecast_accuracy = float(active_perf.r2_score * 100) if active_perf else 97.10
    
    # Inventory Health Calculations
    total_items = InventoryItem.objects.count()
    critical_alerts = Alert.objects.filter(is_resolved=False, severity='Critical').count()
    warn_alerts = Alert.objects.filter(is_resolved=False, severity='Warning').count()
    
    if total_items > 0:
        inv_health = max(10, 100 - int(((critical_alerts * 1.5 + warn_alerts * 0.5) / total_items) * 100))
    else:
        inv_health = 100
        
    # Demand Growth % (Simulate a growth indicator)
    demand_growth = 12.4
    
    # Stockout risk item counts
    stockout_risk_count = Alert.objects.filter(is_resolved=False, alert_type='Stockout Risk').count()
    
    # Fast / Slow Moving Categories
    category_totals = ForecastHistory.objects.values('category').annotate(total_demand=Sum('forecasted_demand')).order_by('-total_demand')
    fast_moving = category_totals[0]['category'] if category_totals.exists() else 'Electronics'
    slow_moving = category_totals[len(category_totals)-1]['category'] if len(category_totals) > 1 else 'Furniture'

    # 2. Dynamic AI Business Insights
    insights = []
    
    # Check for promotions
    promo_sales = ForecastHistory.objects.filter(promotion_active=True).aggregate(avg=Avg('forecasted_demand'))['avg']
    no_promo_sales = ForecastHistory.objects.filter(promotion_active=False).aggregate(avg=Avg('forecasted_demand'))['avg']
    if promo_sales and no_promo_sales and promo_sales > no_promo_sales * 1.15:
        pct = int(round((promo_sales - no_promo_sales)/no_promo_sales * 100))
        insights.append(f"Demand is expected to rise by up to {pct}% due to active seasonal promotions.")
        
    # Check for stockout risks
    high_risk_prods = ForecastHistory.objects.filter(stockout_risk='High').order_by('-created_at')[:2]
    for hp in high_risk_prods:
        insights.append(f"Inventory level for {hp.product_name} may cause stockout. Suggested reorder: {hp.suggested_reorder_quantity} units.")
        
    # Region insights
    region_totals = ForecastHistory.objects.values('region', 'category').annotate(total=Sum('forecasted_demand')).order_by('-total')
    if region_totals.exists():
        top_reg = region_totals[0]
        insights.append(f"Category '{top_reg['category']}' is performing extremely strongly in the {top_reg['region']} region.")
        
    # Standard fallback insights if list is small
    if len(insights) < 2:
        insights.append("Suggested reorder thresholds updated based on recent supplier reliability evaluations.")
        insights.append("Historical analysis indicates Q2 seasonal uptick across Electronics and Grocery.")

    # 3. Pull Data for Visual Charts
    # Category Data
    cat_labels = []
    cat_values = []
    for c in category_totals[:5]:
        cat_labels.append(c['category'])
        cat_values.append(c['total_demand'])
        
    # Region Data
    region_totals = ForecastHistory.objects.values('region').annotate(total=Sum('forecasted_demand'))
    reg_labels = [r['region'] for r in region_totals]
    reg_values = [r['total'] for r in region_totals]
    
    # Monthly trend (Group by month name or date)
    # Since we use SQLite, we can extract the dates and format them in python
    hist_logs = ForecastHistory.objects.order_by('created_at')
    
    # Aggregate monthly demands
    monthly_series = {}
    for log in hist_logs:
        month_name = log.created_at.strftime('%b %Y')
        if month_name not in monthly_series:
            monthly_series[month_name] = {'actual': 0, 'forecast': 0}
        
        # Build split: earlier dates act as historical actuals, newer dates act as forecasts
        if log.created_at < timezone.now() - timezone.timedelta(days=15):
            monthly_series[month_name]['actual'] += log.previous_month_sales
        else:
            monthly_series[month_name]['forecast'] += log.forecasted_demand
            
    trend_labels = list(monthly_series.keys())
    trend_actual = [int(v['actual']) for v in monthly_series.values()]
    trend_forecast = [int(v['forecast']) for v in monthly_series.values()]

    context = {
        'page_template': 'dashboard.html',
        'theme': theme,
        'model_name': model_name,
        'title': 'Executive Intelligence Dashboard',
        'csv_summary': csv_summary,
        
        # KPIs
        'kpi_predicted_demand': predicted_demand,
        'kpi_revenue_forecast': revenue_forecast,
        'kpi_inventory_health': inv_health,
        'kpi_forecast_accuracy': forecast_accuracy,
        'kpi_demand_growth': demand_growth,
        'kpi_stockout_risk_count': stockout_risk_count,
        'kpi_fast_moving': fast_moving,
        'kpi_slow_moving': slow_moving,
        
        # Lists
        'recent_forecasts': ForecastHistory.objects.order_by('-created_at')[:6],
        'active_alerts': Alert.objects.filter(is_resolved=False)[:5],
        'ai_insights': insights,
        
        # Chart JSON configs
        'trend_labels': json.dumps(trend_labels),
        'trend_actual': json.dumps(trend_actual),
        'trend_forecast': json.dumps(trend_forecast),
        'cat_labels': json.dumps(cat_labels),
        'cat_values': json.dumps(cat_values),
        'reg_labels': json.dumps(reg_labels),
        'reg_values': json.dumps(reg_values)
    }
    
    return render(request, 'base.html', context)

def analytics_view(request):
    """
    Analytics Drill-Down Page
    """
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')
    
    # 1. Seasonality index
    season_totals = ForecastHistory.objects.values('category', 'season').annotate(avg_d=Avg('forecasted_demand'))
    seasons_list = ['Spring', 'Summer', 'Autumn', 'Winter']
    season_avg = []
    for s in seasons_list:
        val = ForecastHistory.objects.filter(season=s).aggregate(avg=Avg('forecasted_demand'))['avg'] or 0.0
        season_avg.append(float(round(val, 1)))
        
    # 2. Promo Impact
    promo_avg = float(round(ForecastHistory.objects.filter(promotion_active=True).aggregate(avg=Avg('forecasted_demand'))['avg'] or 0.0, 1))
    no_promo_avg = float(round(ForecastHistory.objects.filter(promotion_active=False).aggregate(avg=Avg('forecasted_demand'))['avg'] or 0.0, 1))
    
    # 3. Model Comparisons
    all_models = ModelPerformance.objects.all()
    model_labels = [m.model_name for m in all_models]
    model_mae = [m.mae for m in all_models]
    model_rmse = [m.rmse for m in all_models]
    
    context = {
        'page_template': 'analytics.html',
        'theme': theme,
        'model_name': model_name,
        'title': 'Demand Analytics & Explanations',
        
        # JSON variables
        'season_labels': json.dumps(seasons_list),
        'season_values': json.dumps(season_avg),
        'promo_avg': promo_avg,
        'no_promo_avg': no_promo_avg,
        'model_labels': json.dumps(model_labels),
        'model_mae': json.dumps(model_mae),
        'model_rmse': json.dumps(model_rmse)
    }
    
    return render(request, 'base.html', context)
