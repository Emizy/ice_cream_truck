import logging
from django.contrib.auth import logout
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.orders.models import Order
from apps.core.models import User, Company, Franchise, IceCreamTruck, Customers
from apps.core.serializer import UserSerializer, UserRegisterSerializer, CompanySerializer, FranchiseSerializer, \
    IceCreamTruckSerializer, FranchiseFormSerializer, ManagerFormSerializer, IceCreamTruckFormSerializer, \
    CustomerFormSerializer, CustomerSerializer
from apps.utils.base import Addon, BaseViewSet, BaseModelViewSet
from apps.utils.permissions import company_access_only
from traceback_with_variables import format_exc

logger = logging.getLogger('core')


def account_logout(request):
    try:
        logout(request)
    except Exception as ex:
        pass
    return redirect('/')


class RegisterViewSet(ViewSet, Addon):
    serializer_class = UserSerializer

    @staticmethod
    def get_request_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()

    @swagger_auto_schema(request_body=UserRegisterSerializer,
                         operation_description="",
                         responses={},
                         operation_summary="USER SIGN-UP ENDPOINT"
                         )
    @action(detail=False, methods=['post'], description='USER SIGN-UP ENDPOINT')
    def register(self, request, *args, **kwargs):
        """
        This endpoint handles creating of a new Company Account for a user on the system
        """
        context = {'status': status.HTTP_201_CREATED}
        try:
            data = self.get_request_data(request)
            logger.info(f'Registering new company on the system with the following information {data}')
            serializer = UserRegisterSerializer(data=data)
            if serializer.is_valid():
                validata_data = serializer.validated_data
                validata_data.update({'username': self.unique_generator(User, 'username', 10)})
                _ = serializer.create(validata_data)
                context.update({'message': 'Account created successfully'})
                logger.info(f'Company created successfully')
            else:
                context.update({'status': status.HTTP_400_BAD_REQUEST, 'errors': serializer.error_messages})
        except Exception as ex:
            logger.info(f'Something went wrong while creating company account due to {str(ex)}')
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])


class UserViewSet(BaseViewSet):
    serializer_class = UserSerializer
    query_set = User.objects.all()

    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="RETRIEVE USER INFORMATION"
    )
    @action(detail=False, methods=['get'], description='Fetch personal information of a logged in user', url_path='me')
    def get_user(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            logger.info(f'Retrieving user information for user {request.user.id}')
            context.update({'data': self.serializer_class(request.user).data})
        except Exception as ex:
            logger.info(f'Something went wrong while fetching user information {request.user.id}')
            context.update({'message': str(ex), 'status': status.HTTP_400_BAD_REQUEST})
        return Response(context, status=context['status'])


class CompanyViewSet(BaseViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    search_fields = ['name']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="List all companies attached to a user"
    )
    def list(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            logger.info(f'Fetching all company attached to user_id {request.user.id}')
            paginate = self.paginator(queryset=self.get_list(self.get_queryset()),
                                      serializer_class=self.serializer_class)
            context.update({'status': status.HTTP_200_OK, 'message': 'OK',
                            'data': paginate})
        except Exception as ex:
            logger.error(f'Error all company attached to user_id {request.user.id} due to {str(ex)}')
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])


class FranchiseViewSet(BaseViewSet, Addon):
    queryset = Franchise.objects.select_related('company', 'user').all()
    serializer_class = FranchiseSerializer
    search_fields = ['name']

    def get_queryset(self):
        return self.queryset

    def get_object(self):
        return get_object_or_404(Franchise, pk=self.kwargs.get('pk'))

    @swagger_auto_schema(
        operation_summary="List all franchise attached to a company"
    )
    @method_decorator(company_access_only(), name='dispatch')
    def list(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            logger.info(f'Fetching all company attached to user_id {request.user.id}')
            paginate = self.paginator(queryset=self.get_list(self.get_queryset()),
                                      serializer_class=self.serializer_class)
            context.update({'status': status.HTTP_200_OK, 'message': 'OK',
                            'data': paginate})
        except Exception as ex:
            logger.error(f'Error all company attached to user_id {request.user.id} due to {str(ex)}')
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @swagger_auto_schema(
        operation_summary="Create a franchise to be attached to a company",
        request_body=FranchiseFormSerializer
    )
    @method_decorator(company_access_only(), name='dispatch')
    def create(self, request, *args, **kwargs):
        """
        This method handles creating of franchise and attaching to a company
        """
        context = {"status": status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            serializer = FranchiseFormSerializer(data=data)
            if serializer.is_valid():
                manager_info = serializer.validated_data.pop('manager_info', '')
                manager, manager_created = self.process_manager(manager_info)
                serializer.validated_data.update({'company': Company.objects.get(user=self.request.user)})

                instance = serializer.create(serializer.validated_data)
                if manager is not None and manager_created is True:
                    instance.user = manager
                    instance.save(update_fields=['user'])
                context.update({'data': self.serializer_class(instance).data, 'status': status.HTTP_201_CREATED})
            else:
                context.update({'errors': serializer.error_messages, 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    def process_manager(self, data):
        try:
            if bool(data) and isinstance(data, dict):
                manager_serializer = ManagerFormSerializer(data=data)
                if not manager_serializer.is_valid():
                    return Response(
                        {'errors': manager_serializer.error_messages, 'status': status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)
                data.update({
                    'username': self.unique_generator(User, 'username', 10),
                })
                user = manager_serializer.create(data)
                return user, True
            else:
                return None, False
        except Exception as ex:
            logger.error(f'Error processing franchise manager creation due to {str(ex)}')
        return None, False

    @swagger_auto_schema(
        operation_summary="Update a franchise to be attached to a company",
        request_body=FranchiseFormSerializer
    )
    def update(self, request, *args, **kwargs):
        """
        This method handle updating of franchise informations
        """
        context = {"status": status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            instance = self.get_object()
            serializer = FranchiseFormSerializer(data=data, instance=instance)
            if serializer.is_valid():
                _ = serializer.update(instance, serializer.validated_data)
                context.update({'data': self.serializer_class(self.get_object()).data, 'status': status.HTTP_200_OK})
            else:
                context.update({'errors': serializer.error_messages, 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @swagger_auto_schema(
        operation_summary="Get franchise full information",
    )
    def retrieve(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            context.update({'data': self.serializer_class(self.get_object()).data})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @swagger_auto_schema(
        operation_summary="Delete franchise information",
    )
    @method_decorator(company_access_only(), name='dispatch')
    def destroy(self, request, *args, **kwargs):
        """
        this method handles deleting of franchise and its associated manager account from the system
        """
        context = {'status': status.HTTP_204_NO_CONTENT}
        try:
            instance = self.get_object()
            instance.user.delete()
            instance.delete()
            context.update({'message': 'Franchise deleted successfully'})
        except Exception as ex:
            context.update({'message': str(ex), 'status': status.HTTP_400_BAD_REQUEST})
        return Response(context, status=context['status'])


class TruckViewSet(BaseModelViewSet):
    queryset = IceCreamTruck.objects.select_related('company', 'franchise').all().order_by('-pk')
    serializer_class = IceCreamTruckSerializer
    search_fields = ['name', 'franchise__name']

    def get_queryset(self):
        if Franchise.objects.filter(user=self.request.user).exists():
            return self.get_franchise_queryset()
        return self.queryset.filter(company__user=self.request.user)

    def get_franchise_queryset(self):
        return self.queryset.filter(franchise__user=self.request.user)

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
        operation_summary="Create an ice cream truck to be attached to a company or franchise if available",
        request_body=IceCreamTruckFormSerializer
    )
    def create(self, request, *args, **kwargs):
        """
        This method handles creating of new ice cream truck to be attached to a company or franchise if available
        """
        context = {'status': status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            serializer = IceCreamTruckFormSerializer(data=data)
            if serializer.is_valid():
                if request.user.groups.filter(name='company').exists():
                    serializer.validated_data.update({'company': Company.objects.get(user=request.user)})
                elif request.user.groups.filter(name='franchise').exists():
                    franchise = Franchise.objects.get(user=request.user)
                    serializer.validated_data.update({'company': franchise.company, 'franchise': franchise})
                else:
                    raise Exception('You currently do not have permission to perform this operation')
                instance = serializer.create(serializer.validated_data)
                context.update({'data': self.serializer_class(instance).data})
            else:
                context.update({'errors': serializer.error_messages, 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @action(detail=True, description='Get truck kpis', url_path='kpi')
    def kpi(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            instance = self.get_object()
            sales = Order.objects.filter(ice_cream_truck=instance).aggregate(total=Sum('total_price'))
            customers = Customers.objects.filter(ice_cream_truck=instance).count()
            context.update(
                {'total_amount': sales['total'] if sales['total'] is not None else 0.0, 'customers': customers})
        except Exception as ex:
            context.update({'message': str(ex), 'status': status.HTTP_400_BAD_REQUEST})
        return Response(context, status=context['status'])

    @swagger_auto_schema(
        operation_summary="Create a customer and add it to ice cream truck",
        request_body=CustomerFormSerializer
    )
    @action(detail=True, methods=['post'], description='Add customer to ice cream truck customers',
            url_path='add_customer')
    def create_customer(self, request, *args, **kwargs):
        context = {'status': status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            instance = self.get_object()
            serializer = CustomerFormSerializer(data=data)
            if serializer.is_valid():
                if Customers.objects.filter(name=serializer.validated_data.get('name')).exists():
                    raise Exception('Customer already exist in your account')
                payload = serializer.validated_data
                payload.update({'ice_cream_truck': instance})
                instance = serializer.create(serializer.validated_data)
                context.update({'data': CustomerSerializer(instance).data})
            else:
                context.update({'errors': serializer.error_messages, 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])
