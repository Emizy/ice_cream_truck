import logging

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from apps.core.models import IceCreamTruck, Franchise, User, Customers
from apps.orders.models import Order
from apps.orders.serializer import OrderSerializer, OrderFormSerializer
from apps.store.models import Store
from apps.utils.base import BaseViewSet

logger = logging.getLogger('order')


class OrderViewSet(BaseViewSet):
    queryset = Order.objects.select_related('customer', 'ice_cream_truck').all()
    serializer_class = OrderSerializer
    search_fields = ['order_number', 'customer__name']

    @staticmethod
    def generate_order_number(abr, queryset):
        if queryset.count() > 0:
            last_order = queryset.last()
            splitter = last_order.order_number.split(f'{abr}-')
            num = splitter[1]
            length_of_inv = len(num)
            int_order = int(num)
            next_num = int_order + 1
            if len(str(next_num)) < length_of_inv:
                rem = length_of_inv - len(str(next_num))
                zero = ["0" for _ in range(1, rem + 1)]
                real_next_num = f'{abr}-{"".join(zero)}{next_num}'
                return real_next_num
            else:
                return next_num
        else:
            return f'{abr}-000001'

    def get_queryset(self):
        if self.request.user.groups.filter(name='franchise').exists():
            return self.get_franchise_queryset()
        return self.queryset.filter(ice_cream_truck__company__user=self.request.user)

    def get_franchise_queryset(self):
        return self.queryset.filter(ice_cream_truck__franchise__user=self.request.user)

    @swagger_auto_schema(
        operation_summary="List all order attached to a user"
    )
    def list(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            logger.info(f'Fetching all order attached to user_id {request.user.id}')
            paginate = self.paginator(queryset=self.get_list(self.get_queryset()),
                                      serializer_class=self.serializer_class)
            context.update({'status': status.HTTP_200_OK, 'message': 'OK',
                            'data': paginate})
        except Exception as ex:
            logger.error(f'Error fetching all order attached to user_id {request.user.id} due to {str(ex)}')
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @swagger_auto_schema(
        operation_summary="Create an order entry for a customer",
        request_body=OrderFormSerializer
    )
    def create(self, request, *args, **kwargs):
        context = {}
        try:
            data = self.get_data(request)
            serializer = OrderFormSerializer(data=data)
            if serializer.is_valid():
                ice_cream_truck = get_object_or_404(IceCreamTruck, pk=serializer.validated_data.get('ice_cream_truck'))
                customer = get_object_or_404(Customers, pk=serializer.validated_data.get('customer'))
                store = get_object_or_404(Store, pk=serializer.validated_data.get('item'),
                                          ice_cream_truck=ice_cream_truck)
                if int(serializer.validated_data.get('qty')) > int(store.qty) or int(store.qty) == 0:
                    return Response({'status': status.HTTP_400_BAD_REQUEST,
                                     'message': "SORRY!"}, status=status.HTTP_400_BAD_REQUEST)
                order = {
                    'ice_cream_truck': ice_cream_truck,
                    'customer': customer,
                    'item': store,
                    'price': store.price,
                    'qty': int(serializer.validated_data.get('qty')),
                    'item_name': store.name,
                    'order_number': self.generate_order_number(ice_cream_truck.name[:2], self.get_queryset())
                }
                instance = serializer.create(order)
                self.update_store(store=store, remove_qty=int(serializer.validated_data.get('qty')))
                context.update({'data': self.serializer_class(instance).data,
                                'status': status.HTTP_201_CREATED,
                                'message': "ENJOY!"})
            else:
                context.update({'errors': serializer.error_messages, 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @staticmethod
    def update_store(store, remove_qty):
        if isinstance(store, Store):
            store.qty -= remove_qty
            store.save(update_fields=['qty'])
