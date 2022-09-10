import uuid
from django.conf import settings
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.utils.pagination import CustomPaginator


class Addon:
    def __init__(self):
        super().__init__()

    def generate_uuid(self, model, column):
        unique = str(uuid.uuid4())
        kwargs = {column: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.generate_uuid(model, column)
        return unique

    def unique_generator(self, model, field, length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
        unique = get_random_string(length=length, allowed_chars=allowed_chars)
        kwargs = {field: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.unique_generator(model, field)
        return unique

    @staticmethod
    def get_model_field(model, data):
        return model.objects.filter(**data)


class CustomFilter(DjangoFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filterset_class(view, queryset)

        if filter_class:
            return filter_class(request.query_params, queryset=queryset, request=request).qs
        return queryset


class BaseViewSet(ViewSet):
    """
    This class inherit from django ViewSet class
    """
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated, ]
    custom_filter_class = CustomFilter()
    search_backends = SearchFilter()
    order_backend = OrderingFilter()
    paginator_class = CustomPaginator()
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    @staticmethod
    def get_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()

    def get_list(self, queryset):
        if 'search' in self.request.query_params:
            query_set = self.search_backends.filter_queryset(request=self.request,
                                                             queryset=queryset,
                                                             view=self)
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(request=self.request,
                                                                 queryset=queryset,
                                                                 view=self)
        else:
            query_set = queryset
        if 'ordering' in self.request.query_params:
            query_set = self.order_backend.filter_queryset(query_set, self.request, self)
        else:
            query_set = query_set.order_by('-pk')
        return query_set

    def paginator(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(queryset, serializer_class, self.request)
        return paginated_data


class BaseModelViewSet(ModelViewSet):
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    @staticmethod
    def get_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()
