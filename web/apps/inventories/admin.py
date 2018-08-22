from django.contrib import admin
from .models import Inventory, InventoryItem
# Register your models here.

admin.site.register(Inventory)
admin.site.register(InventoryItem)
