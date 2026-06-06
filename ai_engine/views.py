import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from inventory.models import InventoryItem
from forecasting.models import ForecastHistory
from forecasting.ml_model import predict_demand
from alerts.models import Alert

def ai_insights_view(request):
    """
    Renders What-If Sim page + Chatbot Assistant interface.
    """
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')
    
    # Send all products to populate the simulation dropdown
    products = InventoryItem.objects.all()
    
    return render(request, 'base.html', {
        'page_template': 'ai_insights.html',
        'theme': theme,
        'model_name': model_name,
        'title': 'AI Insights & Scenario Simulation',
        'products': products
    })

@csrf_exempt
def run_simulation_api(request):
    """
    Simulates predictions based on slider inputs in What-If tab.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            model_name = data.get('model_used', 'LightGBM')
            
            # Predict demand
            pred = predict_demand(data, model_name)
            
            return JsonResponse({
                'success': True,
                'forecasted_demand': pred['forecasted_demand'],
                'revenue_forecast': pred['revenue_forecast'],
                'stockout_risk': pred['stockout_risk'],
                'suggested_reorder_quantity': pred['suggested_reorder_quantity']
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def chatbot_api(request):
    """
    NLP query assistant answering questions on inventory, reorders, alerts, and forecasts.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').lower().strip()
            
            response_text = ""
            
            # 1. Check for product-specific queries
            items = InventoryItem.objects.all()
            matched_item = None
            for item in items:
                if item.product_id.lower() in query or item.product_name.lower() in query:
                    matched_item = item
                    break
                    
            if matched_item:
                # Find latest forecast history for this item
                latest_forecast = ForecastHistory.objects.filter(product_id=matched_item.product_id).order_by('-created_at').first()
                
                response_text = (
                    f"Product Summary: {matched_item.product_name} ({matched_item.product_id}). "
                    f"Current Stock: {matched_item.current_stock} units. "
                    f"Units Ordered: {matched_item.units_ordered} units. "
                    f"Warehouse: {matched_item.warehouse_location}. "
                )
                if latest_forecast:
                    response_text += (
                        f"Latest Forecasted Demand: {latest_forecast.forecasted_demand} units. "
                        f"Demand Trend: {latest_forecast.demand_trend}. "
                        f"Stockout Risk: {latest_forecast.stockout_risk}."
                    )
                    if latest_forecast.suggested_reorder_quantity > 0:
                        response_text += f" Suggested reorder quantity is {latest_forecast.suggested_reorder_quantity} units."
                else:
                    response_text += " No forecasting logs found. Try executing a forecast for this item."
                    
            # 2. Check for alerts / risks
            elif 'alert' in query or 'risk' in query or 'stockout' in query:
                active_alerts = Alert.objects.filter(is_resolved=False)
                if active_alerts.exists():
                    response_text = "I detected the following active alerts: "
                    alert_strs = []
                    for a in active_alerts[:3]:
                        alert_strs.append(f"[{a.severity}] {a.alert_type} on {a.product_name}: {a.message}")
                    response_text += " | ".join(alert_strs)
                else:
                    response_text = "All systems operational! There are currently no active alerts or stockout risks in the inventory database."
                    
            # 3. Check for reorders
            elif 'reorder' in query or 'buy' in query or 'order' in query:
                reorder_items = InventoryItem.objects.filter(current_stock__lte=models.F('safety_stock'))
                if reorder_items.exists():
                    response_text = "The following products require reorders as they have fallen below safety stock thresholds: "
                    reorder_strs = []
                    for item in reorder_items:
                        rec = max(50, item.safety_stock * 2 - item.current_stock)
                        reorder_strs.append(f"{item.product_name} (Current: {item.current_stock}, Rec Reorder: {rec} units)")
                    response_text += ", ".join(reorder_strs)
                    response_text += ". You can quickly trigger reorders from the Inventory Control Panel."
                else:
                    response_text = "No reorders are currently flagged. All inventory levels are above their safety stocks."
                    
            # 4. Check for accuracy / models
            elif 'model' in query or 'accuracy' in query or 'r2' in query:
                active_perf = ModelPerformance.objects.filter(is_active=True).first()
                all_perf = ModelPerformance.objects.all()
                perf_strs = []
                for p in all_perf:
                    perf_strs.append(f"{p.model_name}: R2={p.r2_score*100:.1f}%, MAE={p.mae:.2f}")
                
                response_text = f"Currently active model is {active_perf.model_name if active_perf else 'LightGBM'}. "
                response_text += "Evaluated algorithms on retail dataset: " + " | ".join(perf_strs)
                
            # 5. Default general assistant response
            else:
                response_text = (
                    "Hello! I am your AI Inventory Assistant. I can help you query real-time demand forecasts, "
                    "flag stockout risks, list safety stock violations, or details model scores. "
                    "Try asking me:\n"
                    "- 'Are there any active stockout alerts?'\n"
                    "- 'Which products need to be reordered?'\n"
                    "- 'How is the keyboard performing?'"
                )
                
            return JsonResponse({'success': True, 'response': response_text})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
