import csv
import json
import pandas as pd
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from .models import ForecastHistory
from inventory.models import InventoryItem
from alerts.models import Alert
from ai_engine.models import ModelPerformance
from .ml_model import predict_demand

def hero_view(request):
    """
    Main Hero Section / Entry Point
    """
    # Active settings stored in session
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')
    
    return render(request, 'base.html', {
        'page_template': 'upload_csv.html', # default option screen
        'theme': theme,
        'model_name': model_name,
        'title': 'AI Demand Forecasting Platform'
    })

def manual_forecast_view(request):
    """
    Multi-Step Manual Forecast Form & Result Display
    """
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')
    
    if request.method == 'POST':
        # Retrieve all form parameters
        form_data = {
            'product_name': request.POST.get('product_name', 'Manual Product'),
            'product_id': request.POST.get('product_id', 'PRD-MANUAL'),
            'category': request.POST.get('category', 'Electronics'),
            'region': request.POST.get('region', 'North'),
            'warehouse_location': request.POST.get('warehouse_location', 'WH-Alpha'),
            'selling_price': request.POST.get('selling_price', 100.0),
            'discount_percentage': request.POST.get('discount_percentage', 0.0),
            'competitor_pricing': request.POST.get('competitor_pricing', 100.0),
            'promotion_active': 1 if request.POST.get('promotion_active') == 'on' else 0,
            'marketing_spend': request.POST.get('marketing_spend', 0.0),
            'units_sold': request.POST.get('units_sold', 100.0),
            'previous_month_sales': request.POST.get('previous_month_sales', 100.0),
            'current_inventory_level': request.POST.get('current_inventory_level', 100.0),
            'units_ordered': request.POST.get('units_ordered', 0.0),
            'safety_stock': request.POST.get('safety_stock', 50.0),
            'lead_time': request.POST.get('lead_time', 7.0),
            'supplier_reliability': request.POST.get('supplier_reliability', 0.95),
            'weather_condition': request.POST.get('weather_condition', 'Sunny'),
            'season': request.POST.get('season', 'Summer'),
            'festival_holiday': 1 if request.POST.get('festival_holiday') == 'on' else 0,
            'epidemic_pandemic': 1 if request.POST.get('epidemic_pandemic') == 'on' else 0,
            'inflation_rate': request.POST.get('inflation_rate', 3.0),
            'fuel_price_index': request.POST.get('fuel_price_index', 3.5),
            'economic_condition': request.POST.get('economic_condition', 'Average'),
            'date': request.POST.get('forecast_date', timezone.now().strftime('%Y-%m-%d'))
        }
        
        # Run ML predictions
        pred = predict_demand(form_data, model_name)
        
        # Save to database
        forecast_item = ForecastHistory.objects.create(
            product_id=form_data['product_id'],
            product_name=form_data['product_name'],
            category=form_data['category'],
            region=form_data['region'],
            selling_price=float(form_data['selling_price']),
            discount_percentage=float(form_data['discount_percentage']),
            promotion_active=bool(form_data['promotion_active']),
            marketing_spend=float(form_data['marketing_spend']),
            previous_month_sales=float(form_data['previous_month_sales']),
            forecasted_demand=pred['forecasted_demand'],
            demand_trend=pred['demand_trend'],
            confidence_score=pred['confidence_score'],
            revenue_forecast=pred['revenue_forecast'],
            stockout_risk=pred['stockout_risk'],
            overstock_risk=pred['overstock_risk'],
            suggested_reorder_quantity=pred['suggested_reorder_quantity'],
            model_used=pred['model_used'],
            weather_condition=form_data['weather_condition'],
            season=form_data['season'],
            festival_holiday=bool(form_data['festival_holiday']),
            epidemic_pandemic=bool(form_data['epidemic_pandemic']),
            inflation_rate=float(form_data['inflation_rate']),
            fuel_price_index=float(form_data['fuel_price_index']),
            economic_condition=form_data['economic_condition']
        )
        
        # Trigger dynamic alerts if stock risks are High
        if pred['stockout_risk'] == 'High':
            Alert.objects.create(
                product_id=form_data['product_id'],
                product_name=form_data['product_name'],
                alert_type='Stockout Risk',
                severity='Critical',
                message=f"Manual forecast indicates High Stockout Risk for {form_data['product_name']}. Predicted demand: {pred['forecasted_demand']} units, current stock: {form_data['current_inventory_level']} units."
            )
        elif pred['overstock_risk'] == 'High':
            Alert.objects.create(
                product_id=form_data['product_id'],
                product_name=form_data['product_name'],
                alert_type='Overstock Warning',
                severity='Warning',
                message=f"Manual forecast indicates High Overstock Risk for {form_data['product_name']}. Current stock: {form_data['current_inventory_level']} units, forecasted demand: {pred['forecasted_demand']} units."
            )
            
        # Context including results for plotting charts
        context = {
            'page_template': 'manual_forecast.html',
            'theme': theme,
            'model_name': model_name,
            'title': 'Manual Demand Forecast Engine',
            'form_data': form_data,
            'prediction': pred,
            'forecast_item': forecast_item,
            'success': True,
            'shap_features': list(pred['feature_importance'].keys()),
            'shap_values': list(pred['feature_importance'].values())
        }
        return render(request, 'base.html', context)
        
    return render(request, 'base.html', {
        'page_template': 'manual_forecast.html',
        'theme': theme,
        'model_name': model_name,
        'title': 'Manual Demand Forecast Engine'
    })

def upload_csv_view(request):
    """
    Handles CSV uploader UI and parsing file.
    """
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Parse CSV file via Pandas
        try:
            df = pd.read_csv(csv_file)
            
            # Auto Preprocessing: Check columns and impute defaults if missing
            required_cols = ['selling_price', 'previous_month_sales', 'current_inventory_level']
            for col in required_cols:
                if col not in df.columns:
                    # Impute missing core numerical columns with simple baseline
                    df[col] = 100.0
            
            # Map default fields for any optional columns not in CSV
            optional_cols = {
                'product_name': 'Batch Product',
                'product_id': 'PRD-BATCH',
                'category': 'Electronics',
                'region': 'North',
                'discount_percentage': 0.0,
                'promotion_active': 0,
                'marketing_spend': 0.0,
                'units_sold': 100.0,
                'units_ordered': 0.0,
                'safety_stock': 50.0,
                'lead_time': 7.0,
                'supplier_reliability': 0.95,
                'weather_condition': 'Sunny',
                'season': 'Summer',
                'festival_holiday': 0,
                'epidemic_pandemic': 0,
                'inflation_rate': 3.0,
                'fuel_price_index': 3.5,
                'economic_condition': 'Average',
                'date': timezone.now().strftime('%Y-%m-%d')
            }
            
            for col, default in optional_cols.items():
                if col not in df.columns:
                    df[col] = default
            
            # Run inference row-by-row
            total_rows = len(df)
            categories = df['category'].unique().tolist()
            regions = df['region'].unique().tolist()
            
            total_forecasted_demand = 0
            total_revenue_forecast = 0.0
            high_stockouts_count = 0
            
            for index, row in df.iterrows():
                row_dict = row.to_dict()
                pred = predict_demand(row_dict, model_name)
                
                # Save Forecast record
                ForecastHistory.objects.create(
                    product_id=row_dict['product_id'],
                    product_name=row_dict['product_name'],
                    category=row_dict['category'],
                    region=row_dict['region'],
                    selling_price=float(row_dict['selling_price']),
                    discount_percentage=float(row_dict['discount_percentage']),
                    promotion_active=bool(row_dict['promotion_active']),
                    marketing_spend=float(row_dict['marketing_spend']),
                    previous_month_sales=float(row_dict['previous_month_sales']),
                    forecasted_demand=pred['forecasted_demand'],
                    demand_trend=pred['demand_trend'],
                    confidence_score=pred['confidence_score'],
                    revenue_forecast=pred['revenue_forecast'],
                    stockout_risk=pred['stockout_risk'],
                    overstock_risk=pred['overstock_risk'],
                    suggested_reorder_quantity=pred['suggested_reorder_quantity'],
                    model_used=pred['model_used'],
                    weather_condition=row_dict['weather_condition'],
                    season=row_dict['season'],
                    festival_holiday=bool(row_dict['festival_holiday']),
                    epidemic_pandemic=bool(row_dict['epidemic_pandemic']),
                    inflation_rate=float(row_dict['inflation_rate']),
                    fuel_price_index=float(row_dict['fuel_price_index']),
                    economic_condition=row_dict['economic_condition']
                )
                
                total_forecasted_demand += pred['forecasted_demand']
                total_revenue_forecast += pred['revenue_forecast']
                if pred['stockout_risk'] == 'High':
                    high_stockouts_count += 1
                    
            # Build Preprocessing Report Summary
            summary = {
                'total_rows': total_rows,
                'categories_count': len(categories),
                'regions_count': len(regions),
                'categories_list': ", ".join(categories),
                'regions_list': ", ".join(regions),
                'avg_demand': int(round(total_forecasted_demand / total_rows)) if total_rows > 0 else 0,
                'total_revenue': float(round(total_revenue_forecast, 2)),
                'high_stockouts_count': high_stockouts_count,
                'preprocessing_report': "Dataset cleaned successfully. Missing fields automatically imputed with average parameters. Categorical mappings completed."
            }
            
            # Store in session and redirect to dashboard
            request.session['csv_upload_summary'] = summary
            messages.success(request, "CSV batch dataset successfully processed by AI Engine.")
            return redirect('/dashboard/')
            
        except Exception as e:
            messages.error(request, f"Error processing CSV file: {str(e)}")
            return redirect('/forecast/upload/')

    return render(request, 'base.html', {
        'page_template': 'upload_csv.html',
        'theme': theme,
        'model_name': model_name,
        'title': 'Batch Demand Forecast Engine'
    })

def settings_view(request):
    """
    Settings Page views.
    """
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')
    
    if request.method == 'POST':
        selected_model = request.POST.get('model_name', 'LightGBM')
        selected_theme = request.POST.get('theme', 'dark')
        
        request.session['model_name'] = selected_model
        request.session['theme'] = selected_theme
        
        # Deactivate old model performance active record and set new one
        ModelPerformance.objects.all().update(is_active=False)
        ModelPerformance.objects.filter(model_name=selected_model).update(is_active=True)
        
        messages.success(request, "Settings successfully updated.")
        return redirect('/settings/')
        
    return render(request, 'base.html', {
        'page_template': 'settings.html',
        'theme': theme,
        'model_name': model_name,
        'title': 'System Settings'
    })

@csrf_exempt
def toggle_theme_session(request):
    """
    Asynchronously update theme state in Django sessions.
    """
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        theme = data.get('theme', 'dark')
        request.session['theme'] = theme
        return JsonResponse({'success': True, 'theme': theme})
    return JsonResponse({'success': False}, status=400)
