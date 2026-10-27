from django.db import models
from django.utils import timezone


class ItemMaster(models.Model):
    item_code = models.CharField(max_length=64, unique=True, db_index=True)
    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=128, blank=True, default='')
    unit = models.CharField(max_length=32, default='PCS')  # e.g., PCS, KG, MTR, SET, LTR
    opening_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    unit_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    storage_location = models.CharField(max_length=128, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item_code']
        verbose_name = 'Item Master'
        verbose_name_plural = 'Item Masters'

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"

    @property
    def current_stock(self):
        # Calculate sum of inward movements minus outward movements
        inward_types = [
            StockRegister.TX_RECEIPT,
            StockRegister.TX_PROD_IN,
            StockRegister.TX_SALES_RETURN,
            StockRegister.TX_POS_ADJUSTMENT,
        ]
        outward_types = [
            StockRegister.TX_ISSUE_PROD,
            StockRegister.TX_DISPATCH_SALE,
            StockRegister.TX_SUPP_RETURN,
            StockRegister.TX_NEG_ADJUSTMENT,
        ]
        qty_in = self.movements.filter(transaction_type__in=inward_types).aggregate(
            total=models.Sum('qty_in')
        )['total'] or 0
        qty_out = self.movements.filter(transaction_type__in=outward_types).aggregate(
            total=models.Sum('qty_out')
        )['total'] or 0
        return float(self.opening_stock) + float(qty_in) - float(qty_out)

    @property
    def stock_status(self):
        stock = self.current_stock
        if stock <= 0:
            return 'Out of Stock'
        elif stock <= float(self.reorder_level):
            return 'Reorder Alert'
        return 'Adequate'


class StockRegister(models.Model):
    # Inward
    TX_RECEIPT = 'Receipt'
    TX_PROD_IN = 'Production In'
    TX_SALES_RETURN = 'Sales Return'
    TX_POS_ADJUSTMENT = 'Positive Adjustment'
    # Outward
    TX_ISSUE_PROD = 'Issue to Production'
    TX_DISPATCH_SALE = 'Dispatch/Sale'
    TX_SUPP_RETURN = 'Supplier Return'
    TX_NEG_ADJUSTMENT = 'Negative Adjustment'

    TRANSACTION_CHOICES = [
        (TX_RECEIPT, 'Receipt (Purchase In)'),
        (TX_PROD_IN, 'Production In'),
        (TX_SALES_RETURN, 'Sales Return'),
        (TX_POS_ADJUSTMENT, 'Positive Adjustment'),
        (TX_ISSUE_PROD, 'Issue to Production'),
        (TX_DISPATCH_SALE, 'Dispatch / Sale'),
        (TX_SUPP_RETURN, 'Supplier Return'),
        (TX_NEG_ADJUSTMENT, 'Negative Adjustment'),
    ]

    date = models.DateField(default=timezone.now)
    voucher_ref = models.CharField(max_length=64, blank=True, default='')
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE, related_name='movements')
    transaction_type = models.CharField(max_length=32, choices=TRANSACTION_CHOICES)
    qty_in = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    qty_out = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    unit_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    movement_value = models.DecimalField(max_digits=14, decimal_places=2, default=0.0)
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = 'Stock Register Entry'
        verbose_name_plural = 'Stock Register Entries'

    def save(self, *args, **kwargs):
        # Auto-compute movement value
        qty = self.qty_in if self.qty_in > 0 else self.qty_out
        if self.unit_rate and qty:
            self.movement_value = self.unit_rate * qty
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} | {self.item.item_code} | {self.transaction_type}"


class DailyProduction(models.Model):
    SHIFT_CHOICES = [
        ('Shift A', 'Shift A (Morning)'),
        ('Shift B', 'Shift B (Evening)'),
        ('Shift C', 'Shift C (Night)'),
        ('General', 'General Shift'),
    ]

    date = models.DateField(default=timezone.now)
    shift = models.CharField(max_length=32, choices=SHIFT_CHOICES, default='Shift A')
    product_model = models.CharField(max_length=255)
    product_code = models.CharField(max_length=64, blank=True, default='')
    target_qty = models.IntegerField(default=0)
    produced_qty = models.IntegerField(default=0)
    rejected_qty = models.IntegerField(default=0)
    good_qty = models.IntegerField(default=0)
    unit = models.CharField(max_length=32, default='NOS')
    production_in_stock = models.BooleanField(default=True)
    supervisor = models.CharField(max_length=128, blank=True, default='')
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = 'Daily Production Entry'
        verbose_name_plural = 'Daily Production Entries'

    def save(self, *args, **kwargs):
        self.good_qty = max(0, self.produced_qty - self.rejected_qty)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} | {self.product_model} | Good: {self.good_qty}"


class DailyExpense(models.Model):
    CATEGORY_CHOICES = [
        ('Raw Materials', 'Raw Materials'),
        ('Consumables', 'Consumables & Tools'),
        ('Factory Maintenance', 'Factory Maintenance'),
        ('Electricity & Utilities', 'Electricity & Utilities'),
        ('Freight & Transport', 'Freight & Transport'),
        ('Office & Admin', 'Office & Admin'),
        ('Welfare & Tea', 'Welfare & Tea'),
        ('Contractor Labour', 'Contractor Labour'),
        ('Others', 'Others'),
    ]

    PAYMENT_CHOICES = [
        ('Bank Transfer / NEFT', 'Bank Transfer / NEFT'),
        ('UPI', 'UPI'),
        ('Cheque', 'Cheque'),
        ('Cash', 'Cash'),
        ('Company Card', 'Company Card'),
    ]

    date = models.DateField(default=timezone.now)
    voucher_no = models.CharField(max_length=64, blank=True, default='')
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default='Raw Materials')
    description_paid_to = models.CharField(max_length=255)
    payment_mode = models.CharField(max_length=32, choices=PAYMENT_CHOICES, default='Bank Transfer / NEFT')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    approved_by = models.CharField(max_length=128, blank=True, default='')
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = 'Daily Expense'
        verbose_name_plural = 'Daily Expenses'

    def __str__(self):
        return f"{self.date} | {self.category} | ₹{self.amount}"


class Employee(models.Model):
    DEPARTMENT_CHOICES = [
        ('Production & Assembly', 'Production & Assembly'),
        ('Core & Coil Winding', 'Core & Coil Winding'),
        ('Testing & QA', 'Testing & QA'),
        ('Maintenance', 'Maintenance'),
        ('Stores & Inventory', 'Stores & Inventory'),
        ('Accounts & Admin', 'Accounts & Admin'),
        ('Security & Housekeeping', 'Security & Housekeeping'),
    ]

    employee_id = models.CharField(max_length=32, unique=True, db_index=True)
    employee_name = models.CharField(max_length=255)
    department = models.CharField(max_length=64, choices=DEPARTMENT_CHOICES)
    designation = models.CharField(max_length=128)
    joining_date = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, default='')
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f"{self.employee_id} - {self.employee_name}"


class DailyAttendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Half Day', 'Half Day'),
        ('Leave', 'Leave'),
        ('Weekly Off', 'Weekly Off'),
        ('Holiday', 'Holiday'),
    ]

    date = models.DateField(default=timezone.now)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='Present')
    in_time = models.TimeField(blank=True, null=True)
    out_time = models.TimeField(blank=True, null=True)
    hours = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    overtime_hrs = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'employee')
        ordering = ['-date', 'employee']
        verbose_name = 'Daily Attendance'
        verbose_name_plural = 'Daily Attendances'

    def __str__(self):
        return f"{self.date} | {self.employee.employee_id} | {self.status}"
