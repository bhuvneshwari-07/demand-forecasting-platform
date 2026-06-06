from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Alert

def alerts_view(request):
    """
    Alert list dashboard page
    """
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')
    
    # Separate active alerts and history
    active_alerts = Alert.objects.filter(is_resolved=False).order_by('-created_at')
    resolved_alerts = Alert.objects.filter(is_resolved=True).order_by('-created_at')[:20]
    
    # Alert level indicators
    critical_count = active_alerts.filter(severity='Critical').count()
    warning_count = active_alerts.filter(severity='Warning').count()
    
    context = {
        'page_template': 'alerts.html',
        'theme': theme,
        'model_name': model_name,
        'title': 'System Alerts Center',
        'active_alerts': active_alerts,
        'resolved_alerts': resolved_alerts,
        'critical_count': critical_count,
        'warning_count': warning_count
    }
    
    return render(request, 'base.html', context)

def resolve_alert_view(request, alert_id):
    """
    Mark an active alert as resolved.
    """
    if request.method == 'POST':
        try:
            alert = Alert.objects.get(id=alert_id)
            alert.is_resolved = True
            alert.save()
            messages.success(request, f"Alert for {alert.product_name} marked as resolved.")
        except Alert.DoesNotExist:
            messages.error(request, "Alert not found.")
            
    return redirect('/alerts/')
