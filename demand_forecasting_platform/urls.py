# URL configuration for demand_forecasting_platform project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/6.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
from django.contrib import admin
from django.urls import path
from forecasting import views as forecasting_views
from analytics_dashboard import views as dashboard_views
from inventory import views as inventory_views
from reports import views as reports_views
from alerts import views as alerts_views
from ai_engine import views as ai_engine_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Forecasting views
    path('', forecasting_views.hero_view, name='hero'),
    path('forecast/upload/', forecasting_views.upload_csv_view, name='upload_csv'),
    path('forecast/manual/', forecasting_views.manual_forecast_view, name='manual_forecast'),
    path('settings/', forecasting_views.settings_view, name='settings'),
    path('settings/toggle-theme/', forecasting_views.toggle_theme_session, name='toggle_theme'),
    
    # Dashboard & Analytics views
    path('dashboard/', dashboard_views.dashboard_view, name='dashboard'),
    path('analytics/', dashboard_views.analytics_view, name='analytics'),
    
    # Inventory views
    path('inventory/', inventory_views.inventory_view, name='inventory'),
    path('inventory/reorder/<str:item_id>/', inventory_views.reorder_item_view, name='reorder_item'),
    
    # Reports views
    path('reports/', reports_views.reports_view, name='reports'),
    path('reports/export/csv/', reports_views.export_csv, name='export_csv'),
    path('reports/export/excel/', reports_views.export_excel, name='export_excel'),
    path('reports/export/pdf/', reports_views.export_pdf, name='export_pdf'),
    
    # Alerts views
    path('alerts/', alerts_views.alerts_view, name='alerts'),
    path('alerts/resolve/<int:alert_id>/', alerts_views.resolve_alert_view, name='resolve_alert'),
    
    # AI Engine views
    path('ai-insights/', ai_engine_views.ai_insights_view, name='ai_insights'),
    path('ai-insights/simulate/', ai_engine_views.run_simulation_api, name='simulate_api'),
    path('ai-insights/chatbot/', ai_engine_views.chatbot_api, name='chatbot_api'),
]

