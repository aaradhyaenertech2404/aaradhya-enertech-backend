from rest_framework import serializers
from .models import ItemMaster, StockRegister, DailyProduction, DailyExpense, Employee, DailyAttendance


class ItemMasterSerializer(serializers.ModelSerializer):
    current_stock = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()

    class Meta:
        model = ItemMaster
        fields = '__all__'


class StockRegisterSerializer(serializers.ModelSerializer):
    item_code = serializers.ReadOnlyField(source='item.item_code')
    item_name = serializers.ReadOnlyField(source='item.item_name')
    unit = serializers.ReadOnlyField(source='item.unit')

    class Meta:
        model = StockRegister
        fields = '__all__'


class DailyProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyProduction
        fields = '__all__'


class DailyExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyExpense
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class DailyAttendanceSerializer(serializers.ModelSerializer):
    employee_code = serializers.ReadOnlyField(source='employee.employee_id')
    employee_name = serializers.ReadOnlyField(source='employee.employee_name')
    department = serializers.ReadOnlyField(source='employee.department')

    class Meta:
        model = DailyAttendance
        fields = '__all__'
