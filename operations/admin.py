from django.contrib import admin
from .models import ItemMaster, StockRegister, DailyProduction, DailyExpense, Employee, DailyAttendance


@admin.register(ItemMaster)
class ItemMasterAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'item_name', 'category', 'unit', 'opening_stock', 'current_stock_display', 'reorder_level', 'stock_status_badge')
    search_fields = ('item_code', 'item_name', 'category', 'storage_location')
    list_filter = ('category', 'unit')

    def current_stock_display(self, obj):
        return f"{obj.current_stock:.2f} {obj.unit}"
    current_stock_display.short_description = "Current Stock"

    def stock_status_badge(self, obj):
        return obj.stock_status
    stock_status_badge.short_description = "Status"


@admin.register(StockRegister)
class StockRegisterAdmin(admin.ModelAdmin):
    list_display = ('date', 'voucher_ref', 'item', 'transaction_type', 'qty_in', 'qty_out', 'unit_rate', 'movement_value')
    list_filter = ('transaction_type', 'date')
    search_fields = ('voucher_ref', 'item__item_code', 'item__item_name', 'remarks')


@admin.register(DailyProduction)
class DailyProductionAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'product_model', 'product_code', 'target_qty', 'produced_qty', 'rejected_qty', 'good_qty', 'supervisor')
    list_filter = ('shift', 'date', 'production_in_stock')
    search_fields = ('product_model', 'product_code', 'supervisor', 'remarks')


@admin.register(DailyExpense)
class DailyExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'voucher_no', 'category', 'description_paid_to', 'payment_mode', 'amount', 'approved_by')
    list_filter = ('category', 'payment_mode', 'date')
    search_fields = ('voucher_no', 'description_paid_to', 'approved_by', 'remarks')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'employee_name', 'department', 'designation', 'phone', 'monthly_salary', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('employee_id', 'employee_name', 'phone', 'designation')


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'employee', 'status', 'in_time', 'out_time', 'hours', 'overtime_hrs')
    list_filter = ('status', 'date', 'employee__department')
    search_fields = ('employee__employee_id', 'employee__employee_name', 'remarks')
