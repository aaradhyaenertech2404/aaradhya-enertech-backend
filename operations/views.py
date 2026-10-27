from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
import datetime

from .models import ItemMaster, StockRegister, DailyProduction, DailyExpense, Employee, DailyAttendance
from .serializers import (
    ItemMasterSerializer,
    StockRegisterSerializer,
    DailyProductionSerializer,
    DailyExpenseSerializer,
    EmployeeSerializer,
    DailyAttendanceSerializer
)


class ItemMasterViewSet(viewsets.ModelViewSet):
    queryset = ItemMaster.objects.all()
    serializer_class = ItemMasterSerializer


class StockRegisterViewSet(viewsets.ModelViewSet):
    queryset = StockRegister.objects.all()
    serializer_class = StockRegisterSerializer


class DailyProductionViewSet(viewsets.ModelViewSet):
    queryset = DailyProduction.objects.all()
    serializer_class = DailyProductionSerializer


class DailyExpenseViewSet(viewsets.ModelViewSet):
    queryset = DailyExpense.objects.all()
    serializer_class = DailyExpenseSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class DailyAttendanceViewSet(viewsets.ModelViewSet):
    queryset = DailyAttendance.objects.all()
    serializer_class = DailyAttendanceSerializer


@api_view(['GET'])
def dashboard_summary(request):
    year = int(request.GET.get('year', timezone.now().year))

    # Annual metrics for selected year
    prod_qs = DailyProduction.objects.filter(date__year=year)
    exp_qs = DailyExpense.objects.filter(date__year=year)
    att_qs = DailyAttendance.objects.filter(date__year=year)

    annual_produced = prod_qs.aggregate(total=Sum('produced_qty'))['total'] or 0
    annual_good = prod_qs.aggregate(total=Sum('good_qty'))['total'] or 0
    annual_rejected = prod_qs.aggregate(total=Sum('rejected_qty'))['total'] or 0
    annual_expenses = float(exp_qs.aggregate(total=Sum('amount'))['total'] or 0)

    # Stock on hand summary
    items = ItemMaster.objects.all()
    stock_summary = []
    reorder_alerts_count = 0

    for itm in items:
        cur_stock = itm.current_stock
        st = itm.stock_status
        if st == 'Reorder Alert' or st == 'Out of Stock':
            reorder_alerts_count += 1
        stock_summary.append({
            'id': itm.id,
            'item_code': itm.item_code,
            'item_name': itm.item_name,
            'category': itm.category,
            'unit': itm.unit,
            'opening_stock': float(itm.opening_stock),
            'closing_stock': cur_stock,
            'reorder_level': float(itm.reorder_level),
            'unit_rate': float(itm.unit_rate),
            'stock_value': cur_stock * float(itm.unit_rate),
            'status': st
        })

    # Monthly breakdown for the year
    months_data = []
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    for m in range(1, 13):
        m_prod = prod_qs.filter(date__month=m).aggregate(
            prod=Sum('produced_qty'),
            good=Sum('good_qty'),
            rej=Sum('rejected_qty')
        )
        m_exp = exp_qs.filter(date__month=m).aggregate(total=Sum('amount'))['total'] or 0
        m_att = att_qs.filter(date__month=m)

        months_data.append({
            'month': month_names[m - 1],
            'month_num': m,
            'produced_qty': m_prod['prod'] or 0,
            'good_qty': m_prod['good'] or 0,
            'rejected_qty': m_prod['rej'] or 0,
            'expenses': float(m_exp),
            'present_days': m_att.filter(status='Present').count(),
            'absent_days': m_att.filter(status='Absent').count(),
            'half_days': m_att.filter(status='Half Day').count(),
        })

    # Active employee count
    active_employees = Employee.objects.filter(is_active=True).count()

    return Response({
        'year': year,
        'annual_production': annual_produced,
        'annual_good_output': annual_good,
        'annual_rejected': annual_rejected,
        'annual_expenses': annual_expenses,
        'active_employees': active_employees,
        'total_items_tracked': items.count(),
        'reorder_alerts_count': reorder_alerts_count,
        'stock_summary': stock_summary,
        'monthly_data': months_data,
    })
