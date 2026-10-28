import os
import django
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from operations.models import ItemMaster, StockRegister, DailyProduction, DailyExpense, Employee, DailyAttendance

# 1. Administrator User (Single Role)
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@aaradhyaenertech.com', 'admin123')
    print("Created administrator superuser: admin / admin123")
else:
    u = User.objects.get(username='admin')
    u.is_superuser = True
    u.is_staff = True
    u.set_password('admin123')
    u.save()
    print("Updated administrator: admin / admin123")
User.objects.filter(username='staff').delete()
User.objects.filter(username='superuser').delete()

# 2. Seed Item Master
raw_materials = [
    ("CRGO-M4-027", "CRGO Silicon Steel Laminations (0.27mm M4)", "Core Laminations", "KG", 4500, 285.00, 1200, "Bay 1 - Core Stacking", "Prime Grade"),
    ("EC-COPPER-STRIP", "Electrolytic Copper Strips (Paper Insulated)", "Winding Conductor", "KG", 3200, 840.00, 800, "Bay 2 - Coil Winding", "99.99% Conductivity"),
    ("EC-ALUM-WIRE", "EC Grade Aluminum Winding Wire", "Winding Conductor", "KG", 1800, 310.00, 500, "Bay 2 - Coil Winding", "Grade 1"),
    ("TRF-OIL-IS335", "Transformer Insulating Mineral Oil (IS 335)", "Insulation Oil", "LTR", 8500, 95.00, 2500, "Tank Farm - Section B", "Dielectric BDV > 65kV"),
    ("MS-TANK-630KVA", "Mild Steel Fabricated Tank 630 kVA with Radiator Fins", "Tanks & Enclosures", "SET", 12, 45000.00, 4, "Bay 4 - Tanking Yard", "Shot blasted & epoxy primed"),
    ("BUSHING-HV-11KV", "11kV High Voltage Porcelain Bushings with Arcing Horns", "Bushings & Hardware", "PCS", 48, 1450.00, 16, "Store Room A - Rack 3", "IS 2099 / IS 7421"),
    ("BUSHING-LV-1KV", "1.1kV Low Voltage Brass Stem Bushings", "Bushings & Hardware", "PCS", 64, 620.00, 24, "Store Room A - Rack 3", "Brass threaded"),
    ("BUCHHOLZ-RELAY-1", "Double Float Buchholz Gas Relay 50mm", "Protection & Relays", "PCS", 8, 4800.00, 3, "Store Room B - Safety Rack", "Mercury contacts"),
    ("SILICA-GEL-BRTH", "Silica Gel Breather Unit 1.0 KG with Oil Cup", "Accessories", "PCS", 22, 950.00, 8, "Store Room B - Rack 1", "Self-indicating blue gel"),
    ("MDI-TEMP-GAUGE", "Magnetic Oil Level Indicator & Dial Thermometer", "Instrumentation", "PCS", 14, 2100.00, 5, "Store Room B - Instrument Cabinet", "Range 0-120C with alarm"),
]

for code, name, cat, unit, open_st, rate, reorder, loc, notes in raw_materials:
    ItemMaster.objects.get_or_create(
        item_code=code,
        defaults={
            'item_name': name,
            'category': cat,
            'unit': unit,
            'opening_stock': Decimal(open_st),
            'unit_rate': Decimal(rate),
            'reorder_level': Decimal(reorder),
            'storage_location': loc,
            'notes': notes,
        }
    )
print(f"Item Master seeded ({len(raw_materials)} items).")

# 3. Seed Stock Movements
crgo = ItemMaster.objects.get(item_code="CRGO-M4-027")
cu = ItemMaster.objects.get(item_code="EC-COPPER-STRIP")
oil = ItemMaster.objects.get(item_code="TRF-OIL-IS335")

if not StockRegister.objects.exists():
    StockRegister.objects.create(
        date=date(2026, 10, 5),
        voucher_ref="PO-2026-104",
        item=crgo,
        transaction_type=StockRegister.TX_RECEIPT,
        qty_in=Decimal(1500),
        unit_rate=crgo.unit_rate,
        movement_value=Decimal(1500) * crgo.unit_rate,
        remarks="Fresh consignment from POSCO India"
    )
    StockRegister.objects.create(
        date=date(2026, 10, 12),
        voucher_ref="ISSUE-PRD-88",
        item=crgo,
        transaction_type=StockRegister.TX_ISSUE_PROD,
        qty_out=Decimal(800),
        unit_rate=crgo.unit_rate,
        movement_value=Decimal(800) * crgo.unit_rate,
        remarks="Issued to Core Assembly Bay for Batch #630-OCT"
    )
    StockRegister.objects.create(
        date=date(2026, 10, 8),
        voucher_ref="ISSUE-PRD-89",
        item=cu,
        transaction_type=StockRegister.TX_ISSUE_PROD,
        qty_out=Decimal(650),
        unit_rate=cu.unit_rate,
        movement_value=Decimal(650) * cu.unit_rate,
        remarks="Issued to Coil Winding Section"
    )
    StockRegister.objects.create(
        date=date(2026, 10, 15),
        voucher_ref="PO-2026-109",
        item=oil,
        transaction_type=StockRegister.TX_RECEIPT,
        qty_in=Decimal(2000),
        unit_rate=oil.unit_rate,
        movement_value=Decimal(2000) * oil.unit_rate,
        remarks="Direct tanker supply with test certificate"
    )
    print("Stock Register seeded.")

# 4. Seed Production
if not DailyProduction.objects.exists():
    DailyProduction.objects.create(
        date=date(2026, 10, 20),
        shift="Shift A",
        product_model="Distribution Transformer 100 kVA 11kV/433V (IS 1180 L2)",
        product_code="DT-100KVA-11",
        target_qty=4,
        produced_qty=4,
        rejected_qty=0,
        good_qty=4,
        unit="NOS",
        production_in_stock=True,
        supervisor="R. K. Sharma (Works Head)",
        remarks="Routine pressure & insulation BDV test cleared 100%"
    )
    DailyProduction.objects.create(
        date=date(2026, 10, 22),
        shift="Shift A",
        product_model="Distribution Transformer 250 kVA 11kV/433V (BEE 2-Star)",
        product_code="DT-250KVA-11",
        target_qty=3,
        produced_qty=3,
        rejected_qty=0,
        good_qty=3,
        unit="NOS",
        production_in_stock=True,
        supervisor="Mahesh Chand",
        remarks="High voltage withstand tested in computerized lab"
    )
    DailyProduction.objects.create(
        date=date(2026, 10, 24),
        shift="Shift B",
        product_model="Substation Power Transformer 630 kVA 33kV Class",
        product_code="PT-630KVA-33",
        target_qty=2,
        produced_qty=2,
        rejected_qty=0,
        good_qty=2,
        unit="NOS",
        production_in_stock=True,
        supervisor="R. K. Sharma",
        remarks="Under oil vacuum filling and heat run test"
    )
    print("Daily Production seeded.")

# 5. Seed Daily Expenses
if not DailyExpense.objects.exists():
    DailyExpense.objects.create(
        date=date(2026, 10, 18),
        voucher_no="EXP-26-891",
        category="Consumables",
        description_paid_to="National Industrial Gas Agency (Nitrogen Purging)",
        payment_mode="Bank Transfer / NEFT",
        amount=Decimal(18500.00),
        approved_by="Director - Finance",
        remarks="Refilling 12 nitrogen cylinders for dry-vacuum ovens"
    )
    DailyExpense.objects.create(
        date=date(2026, 10, 21),
        voucher_no="EXP-26-892",
        category="Factory Maintenance",
        description_paid_to="Rajasthan Crane & Hoist Servicing",
        payment_mode="Cheque",
        amount=Decimal(24000.00),
        approved_by="Works Head",
        remarks="Annual load testing and overhaul of 15T overhead EOT crane"
    )
    DailyExpense.objects.create(
        date=date(2026, 10, 25),
        voucher_no="EXP-26-893",
        category="Electricity & Utilities",
        description_paid_to="JVVNL Bindayaka Industrial Substation",
        payment_mode="Bank Transfer / NEFT",
        amount=Decimal(142600.00),
        approved_by="Director - Operations",
        remarks="Factory HT industrial tariff bill for Sept-Oct cycle"
    )
    print("Daily Expenses seeded.")

# 6. Seed Employees
employees = [
    ("EMP-001", "R. K. Sharma", "Testing & QA", "Quality Assurance & Works Head", "2018-04-01", "+91-9414051052", 65000),
    ("EMP-002", "Mahesh Chand Verma", "Core & Coil Winding", "Senior Winding Supervisor", "2019-07-15", "+91-7976422576", 42000),
    ("EMP-003", "Prakash Saini", "Production & Assembly", "Core Stacking Lead Fitter", "2021-02-10", "+91-9829012345", 28000),
    ("EMP-004", "Vikram Rathore", "Stores & Inventory", "Stores & Material Manager", "2020-11-01", "+91-9785123456", 35000),
    ("EMP-005", "Dinesh Kumar", "Maintenance", "Electrical Maintenance Incharge", "2022-01-18", "+91-9654123890", 30000),
]

for emp_id, name, dept, desig, j_date, ph, sal in employees:
    Employee.objects.get_or_create(
        employee_id=emp_id,
        defaults={
            'employee_name': name,
            'department': dept,
            'designation': desig,
            'joining_date': j_date,
            'phone': ph,
            'monthly_salary': Decimal(sal),
            'is_active': True,
        }
    )
print(f"Employees seeded ({len(employees)} staff).")

# 7. Seed Daily Attendance
if not DailyAttendance.objects.exists():
    for emp in Employee.objects.all():
        DailyAttendance.objects.create(
            date=date(2026, 10, 26),
            employee=emp,
            status='Present',
            hours=Decimal(8.5),
            overtime_hrs=Decimal(0.5) if emp.department == 'Core & Coil Winding' else Decimal(0.0),
            remarks="Normal duty completed"
        )
    print("Daily Attendance seeded.")

print("All Aaradhya Enertech operations seed data successfully initialized!")
