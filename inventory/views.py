from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import models
from .models import InventoryItem
from alerts.models import Alert

def inventory_view(request):
    """
    Inventory status page view
    """
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')
    
    items = InventoryItem.objects.all()
    
    # Calculate summary metrics
    total_products = items.count()
    total_stock_value = 0.0
    low_stock_count = 0
    out_of_stock_count = 0
    
    for item in items:
        # Categorize item stock health
        if item.current_stock == 0:
            item.status = "Out of Stock"
            item.badge_class = "danger"
            out_of_stock_count += 1
        elif item.current_stock <= item.safety_stock:
            item.status = "Low Stock"
            item.badge_class = "warning"
            low_stock_count += 1
        else:
            item.status = "Optimal"
            item.badge_class = "success"
            
    context = {
        'page_template': 'inventory.html',
        'theme': theme,
        'model_name': model_name,
        'title': 'Inventory Intelligence Control',
        'inventory_items': items,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count
    }
    
    return render(request, 'base.html', context)

def reorder_item_view(request, item_id):
    """
    Action to trigger reordering of stock units.
    """
    if request.method == 'POST':
        try:
            item = InventoryItem.objects.get(product_id=item_id)
            # Reorder an amount equal to double safety stock
            reorder_qty = item.safety_stock * 2
            item.units_ordered += reorder_qty
            item.save()
            
            # Resolve any matching low stock alerts for this product
            Alert.objects.filter(product_id=item_id, alert_type='Low Inventory').update(is_resolved=True)
            
            messages.success(request, f"Reorder request for {reorder_qty} units of {item.product_name} sent to suppliers.")
        except InventoryItem.DoesNotExist:
            messages.error(request, "Product not found.")
            
    return redirect('/inventory/')
