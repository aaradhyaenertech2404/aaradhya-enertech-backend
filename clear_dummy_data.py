import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from operations.models import ItemMaster, StockRegister, DailyProduction, DailyExpense, Employee, DailyAttendance

print("Clearing operations tables...")
StockRegister.objects.all().delete()
DailyProduction.objects.all().delete()
DailyExpense.objects.all().delete()
DailyAttendance.objects.all().delete()
Employee.objects.all().delete()
ItemMaster.objects.all().delete()

print("Remaining counts:")
print("Items:", ItemMaster.objects.count())
print("Stock movements:", StockRegister.objects.count())
print("Production:", DailyProduction.objects.count())
print("Expenses:", DailyExpense.objects.count())
print("Employees:", Employee.objects.count())
print("Attendance:", DailyAttendance.objects.count())
print("Done! Database is now completely clean.")
