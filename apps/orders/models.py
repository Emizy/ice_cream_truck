from django.db import models

from apps.core.models import Customers
from apps.store.models import Store
from apps.utils.abstract_class import IceCreamTruckRelatedModel, AbstractUUID


class Order(IceCreamTruckRelatedModel, AbstractUUID):
    customer = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer')
    order_number = models.CharField(max_length=20)
    item = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, related_name='store')
    item_name = models.CharField(max_length=255, null=True, blank=True,
                                 help_text='Field will be auto populated if item is being deleted i.e'
                                           'primarily for item name tracking')
    price = models.FloatField(default=0.0)
    qty = models.PositiveIntegerField(default=1)
    total_price = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.order_number} | {self.customer.name} | {self.ice_cream_truck.name}'

    class Meta:
        db_table = 'order'
        verbose_name_plural = 'Orders'

    def save(self, *args, **kwargs):
        if self.item:
            self.total_price = self.item.price * self.qty
        return super().save(*args, **kwargs)
