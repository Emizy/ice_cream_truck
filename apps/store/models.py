from apps.utils.abstract_class import IceCreamTruckRelatedModel, AbstractUUID
from django.db import models


class Store(IceCreamTruckRelatedModel, AbstractUUID):
    flavor = models.ForeignKey('Flavor', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default='')
    qty = models.PositiveIntegerField(default=0)
    price = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'store'
        verbose_name_plural = 'Stores'


class Flavor(IceCreamTruckRelatedModel, AbstractUUID):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'flavor'
        verbose_name_plural = 'Flavors'
