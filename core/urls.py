from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Aaradhya Enertech Industries"
admin.site.site_title = "Operations & Inventory Portal"
admin.site.index_title = "Daily Operations & Factory Workbook"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('operations.urls')),
]
