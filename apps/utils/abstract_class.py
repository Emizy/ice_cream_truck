import uuid

from django.db import models


class AbstractUUID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class IceCreamTruckRelatedModel(models.Model):
    """Abstract class used by models that belong to a IceCreamTruck"""
    ice_cream_truck = models.ForeignKey(
        "core.IceCreamTruck",
        related_name="%(class)s",
        on_delete=models.CASCADE,
        editable=True,
    )

    class Meta:
        abstract = True
