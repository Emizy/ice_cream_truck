from rest_framework import serializers

from apps.core.serializer import IceCreamTruckSerializer, UserSerializer
from apps.orders.models import Order
from apps.store.models import Store


class OrderSerializer(serializers.ModelSerializer):
    ice_cream_truck = IceCreamTruckSerializer(read_only=True)
    customer = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'ice_cream_truck', 'customer', 'order_number', 'item', 'item_name', 'price', 'qty']


class OrderFormSerializer(serializers.Serializer):
    customer = serializers.CharField(required=True)
    ice_cream_truck = serializers.CharField(required=True)
    item = serializers.CharField(required=True, help_text='Id of the ice cream in store')
    qty = serializers.IntegerField(required=True)

    def create(self, validated_data):
        instance = Order.objects.create(**validated_data)
        return instance

    def validate(self, attrs):
        if attrs.get('qty') <= 0:
            raise serializers.ValidationError('Order quantity must be greater than 0')
        return attrs
