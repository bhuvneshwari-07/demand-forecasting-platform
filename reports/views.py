import csv
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from forecasting.models import ForecastHistory
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def reports_view(request):
    """
    Renders filtered tabular forecast history report page.
    """
    theme = request.session.get('theme', 'dark')
    model_name = request.session.get('model_name', 'LightGBM')
    
    queryset = ForecastHistory.objects.order_by('-created_at')
    
    # 1. Apply Filters
    category = request.GET.get('category')
    region = request.GET.get('region')
    search_query = request.GET.get('search')
    
    if category:
        queryset = queryset.filter(category=category)
    if region:
        queryset = queryset.filter(region=region)
    if search_query:
        queryset = queryset.filter(product_name__icontains=search_query) | queryset.filter(product_id__icontains=search_query)
        
    # 2. Pagination
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ['Electronics', 'Grocery', 'Clothing', 'Toys', 'Furniture']
    regions = ['North', 'South', 'East', 'West']
    
    context = {
        'page_template': 'reports.html',
        'theme': theme,
        'model_name': model_name,
        'title': 'Historical Forecast Reports Control',
        'page_obj': page_obj,
        'categories': categories,
        'regions': regions,
        'selected_category': category,
        'selected_region': region,
        'search_query': search_query
    }
    
    return render(request, 'base.html', context)

def filter_queryset_helper(request):
    queryset = ForecastHistory.objects.order_by('-created_at')
    category = request.GET.get('category')
    region = request.GET.get('region')
    search_query = request.GET.get('search')
    if category:
        queryset = queryset.filter(category=category)
    if region:
        queryset = queryset.filter(region=region)
    if search_query:
        queryset = queryset.filter(product_name__icontains=search_query) | queryset.filter(product_id__icontains=search_query)
    return queryset

def export_csv(request):
    """
    Export filtered dataset to CSV.
    """
    queryset = filter_queryset_helper(request)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="forecast_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Product ID', 'Product Name', 'Category', 'Region', 'Price', 
        'Discount %', 'Promo Active', 'Forecasted Demand', 'Trend', 
        'Confidence %', 'Revenue Forecast', 'Stockout Risk', 'Reorder Qty', 'Created At'
    ])
    
    for item in queryset:
        writer.writerow([
            item.product_id, item.product_name, item.category, item.region, item.selling_price,
            item.discount_percentage, item.promotion_active, item.forecasted_demand, item.demand_trend,
            item.confidence_score, item.revenue_forecast, item.stockout_risk, item.suggested_reorder_quantity,
            item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    return response

def export_excel(request):
    """
    Export filtered dataset to Excel using openpyxl.
    """
    queryset = filter_queryset_helper(request)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="forecast_report.xlsx"'
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Forecast Report"
    
    headers = [
        'Product ID', 'Product Name', 'Category', 'Region', 'Price ($)', 
        'Discount (%)', 'Promo Active', 'Forecasted Demand (Units)', 'Trend', 
        'Confidence (%)', 'Revenue Forecast ($)', 'Stockout Risk', 'Suggested Reorder Qty', 'Generated Date'
    ]
    ws.append(headers)
    
    for item in queryset:
        ws.append([
            item.product_id, item.product_name, item.category, item.region, item.selling_price,
            item.discount_percentage, "Yes" if item.promotion_active else "No", item.forecasted_demand, item.demand_trend,
            item.confidence_score, item.revenue_forecast, item.stockout_risk, item.suggested_reorder_quantity,
            item.created_at.strftime('%Y-%m-%d')
        ])
        
    # Simple autosize column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = col[0].column_letter
        ws.column_dimensions[col_letter].width = max(max_len + 3, 10)
        
    wb.save(response)
    return response

def export_pdf(request):
    """
    Export filtered dataset to a professional PDF report using reportlab.
    """
    queryset = filter_queryset_helper(request)[:30] # Limit to top 30 rows in PDF for layout margins
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="forecast_report.pdf"'
    
    # Setup document configuration
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', 
        parent=styles['Heading1'], 
        textColor=colors.HexColor('#047857'), # green
        fontSize=20, 
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'SubStyle', 
        parent=styles['Normal'], 
        textColor=colors.HexColor('#4b5563'), 
        fontSize=10, 
        spaceAfter=25
    )
    
    story.append(Paragraph("AI Demand Forecasting Platform - Forecast History Report", title_style))
    story.append(Paragraph(f"Generated at: {queryset[0].created_at.strftime('%Y-%m-%d %H:%M:%S') if queryset.exists() else 'N/A'}. Limited to top 30 records.", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Table data
    table_data = [[
        'Product ID', 'Name', 'Category', 'Price', 'Promo', 'Forecast', 'Trend', 'Revenue', 'Stockout'
    ]]
    
    for item in queryset:
        table_data.append([
            item.product_id,
            item.product_name[:15] + ".." if len(item.product_name) > 15 else item.product_name,
            item.category,
            f"${item.selling_price:.2f}",
            "Yes" if item.promotion_active else "No",
            str(item.forecasted_demand),
            item.demand_trend,
            f"${item.revenue_forecast:.2f}",
            item.stockout_risk
        ])
        
    # Table Styling
    report_table = Table(table_data, colWidths=[65, 95, 65, 50, 45, 55, 50, 65, 50])
    report_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
    ]))
    
    story.append(report_table)
    doc.build(story)
    
    return response
