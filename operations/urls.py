from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ItemMasterViewSet,
    StockRegisterViewSet,
    DailyProductionViewSet,
    DailyExpenseViewSet,
    EmployeeViewSet,
    DailyAttendanceViewSet,
    dashboard_summary
)

router = DefaultRouter()
router.register(r'items', ItemMasterViewSet)
router.register(r'stock', StockRegisterViewSet)
router.register(r'production', DailyProductionViewSet)
router.register(r'expenses', DailyExpenseViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'attendance', DailyAttendanceViewSet)

urlpatterns = [
    path('dashboard/', dashboard_summary, name='dashboard-summary'),
    path('', include(router.urls)),
]
