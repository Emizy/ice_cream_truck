import logging

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.models import Franchise, IceCreamTruck
from apps.store.models import Store, Flavor
from apps.store.serializer import StoreSerializer, FlavorSerializer, StoreFormSerializer, AddStockSerializer
from apps.utils.base import BaseModelViewSet
from traceback_with_variables import format_exc

logger = logging.getLogger('store')


class StoreViewSet(BaseModelViewSet):
    queryset = Store.objects.select_related('ice_cream_truck', 'flavor').all().order_by('pk')
    serializer_class = StoreSerializer
    search_fields = ['name']
    filter_fields = ['flavor__name', 'ice_cream_truck_id']

    def get_queryset(self):
        if self.request.user.groups.filter(name='franchise').exists():
            return self.get_franchise_queryset()
        return self.queryset.filter(ice_cream_truck__company__user=self.request.user)

    def get_franchise_queryset(self):
        return self.queryset.filter(ice_cream_truck__franchise__user=self.request.user)

    @swagger_auto_schema(
        operation_summary="List all ice-cream truck"
    )
    def list(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            logger.info(f'Fetching all ice cream truck  for user_id {request.user.id}')
            context.update({'status': status.HTTP_200_OK, 'message': 'OK',
                            'data': super().list(request, *args, **kwargs).data})
        except Exception as ex:
            logger.error(f'Error fetching all ice cream truck for user_id {request.user.id} due to {str(ex)}')
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @swagger_auto_schema(
        operation_summary="Create new ice cream stock ",
        request_body=StoreFormSerializer
    )
    def create(self, request, *args, **kwargs):
        context = {'status': status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            serializer = StoreFormSerializer(data=data)
            if serializer.is_valid():
                truck = get_object_or_404(IceCreamTruck, pk=serializer.validated_data.get('ice_cream_truck'))
                flavor = get_object_or_404(Flavor, pk=serializer.validated_data.get('flavor'), ice_cream_truck=truck)
                serializer.validated_data.update({'ice_cream_truck': truck, 'flavor': flavor})
                if Store.objects.filter(name=serializer.validated_data.get('name'), ice_cream_truck=truck).exists():
                    raise Exception('Ice cream with this name already exist inside your store')
                instance = serializer.create(serializer.validated_data)
                context.update({'data': self.serializer_class(instance).data})
            else:
                context.update({'errors': serializer.error_messages, 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @swagger_auto_schema(
        operation_summary="Add new stock to ice cream store ",
        request_body=AddStockSerializer
    )
    @action(detail=True, methods=['put'], description='Add stock to ice cream store', url_path='stock')
    def add_stock(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            instance = self.get_object()
            serializer = AddStockSerializer(data=self.get_data(request))
            if serializer.is_valid():
                instance = serializer.update(instance, serializer.validated_data)
                context.update({'status': status.HTTP_200_OK, 'message': 'Stock added',
                                'data': self.serializer_class(instance).data})
            else:
                context.update({'errors': serializer.error_messages, 'status': status.HTTP_400_BAD_REQUEST})
                print(context)
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
            logger.error(format_exc(ex))
        return Response(context, status=context['status'])

    @swagger_auto_schema(
        operation_summary="Update ice cream in store ",
        request_body=StoreFormSerializer
    )
    def update(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            instance = self.get_object()
            serializer = StoreFormSerializer(data=data, instance=instance)
            if serializer.is_valid():
                truck = get_object_or_404(IceCreamTruck, pk=serializer.validated_data.get('ice_cream_truck'))
                serializer.validated_data.update({'ice_cream_truck': truck})
                payload = serializer.validated_data
                if serializer.validated_data.get('flavor'):
                    flavor = get_object_or_404(Flavor, pk=serializer.validated_data.get('flavor'),
                                               ice_cream_truck=truck)
                    payload.update({'flavor': flavor})
                payload.update({'ice_cream_truck': truck})
                _ = serializer.update(instance=instance, validated_data=serializer.validated_data)
                context.update({'data': self.serializer_class(self.get_object()).data})
            else:
                context.update({'errors': serializer.error_messages, 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])


class FlavorViewSet(BaseModelViewSet):
    queryset = Flavor.objects.select_related('ice_cream_truck').all().order_by('pk')
    serializer_class = FlavorSerializer
    search_fields = ['name']
    filter_fields = ['ice_cream_truck_id']

    def get_queryset(self):
        if Franchise.objects.filter(user=self.request.user).exists():
            return self.get_franchise_queryset()
        return self.queryset.filter(ice_cream_truck__company__user=self.request.user)

    def get_franchise_queryset(self):
        return self.queryset.filter(ice_cream_truck__franchise__user=self.request.user)
