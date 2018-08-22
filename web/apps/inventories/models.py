from django.db import models
from web.apps.users.models import DiscordUser
from web.apps.items.models import ItemType, Item
# Create your models here.


class Inventory(models.Model):
    type = models.ForeignKey(ItemType, on_delete=models.CASCADE, related_name='inventories')
    user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, related_name='inventories')


class InventoryItem(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='inventory_items')
    obtained_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='inventory_items')
    stat = models.IntegerField()
