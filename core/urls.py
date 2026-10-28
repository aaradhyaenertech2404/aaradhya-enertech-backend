from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

admin.site.site_header = "Aaradhya Enertech Industries"
admin.site.site_title = "Operations & Inventory Portal"
admin.site.index_title = "Daily Operations & Factory Workbook"

def home_view(request):
    return JsonResponse({
        "status": "online",
        "service": "Aaradhya Enertech Industries Backend API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin/",
            "api_dashboard": "/api/dashboard/",
            "api_items": "/api/items/",
            "api_stock": "/api/stock/",
            "api_production": "/api/production/",
            "api_expenses": "/api/expenses/",
            "api_employees": "/api/employees/",
            "api_attendance": "/api/attendance/"
        }
    })

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('operations.urls')),
]
