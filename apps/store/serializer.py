from rest_framework import serializers

from apps.core.serializer import IceCreamTruckSerializer
from apps.store.models import Store, Flavor


class FlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flavor
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    flavor = FlavorSerializer(read_only=True)
    ice_cream_truck = IceCreamTruckSerializer(read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'qty', 'price', 'description', 'flavor', 'ice_cream_truck']


class StoreFormSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    qty = serializers.IntegerField(required=True)
    description = serializers.CharField(required=False)
    price = serializers.FloatField(required=True)
    flavor = serializers.CharField(required=False)
    ice_cream_truck = serializers.CharField(required=True, help_text="This refer to the id of the ice cream truck")

    def create(self, validated_data):
        instance = Store.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        _ = Store.objects.filter(id=instance.id).update(**validated_data)
        return instance


class AddStockSerializer(serializers.Serializer):
    qty = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        instance.qty += int(validated_data.get('qty'))
        instance.save(update_fields=['qty'])
        return instance
