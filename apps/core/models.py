from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.utils.abstract_class import AbstractUUID

from apps.utils.enums import UserTypeEnum


class User(AbstractUser, AbstractUUID):
    """
    User models
    """
    user_type = models.CharField(max_length=25, choices=UserTypeEnum.choices(), default=UserTypeEnum.COMPANY_OWNER)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = 'user'
        ordering = ('-date_joined',)
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.id} {self.username} {self.name}"


class Company(AbstractUUID):
    """
    Company model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_ref')
    name = models.CharField(max_length=255)
    description = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} | {self.user.get_full_name()}'

    class Meta:
        db_table = 'company'
        verbose_name_plural = 'Companies'


class Franchise(AbstractUUID):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_franchise_ref')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='franchise_rep',
                                help_text='This field indicate the manager in charge of the franchise', null=True,
                                blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} | {self.user.get_full_name()}'

    class Meta:
        db_table = 'franchise'
        verbose_name_plural = 'Franchise'


class IceCreamTruck(AbstractUUID):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_ice_trunk_ref')
    franchise = models.ForeignKey(Franchise, on_delete=models.SET_NULL, related_name='franchise_ref', null=True,
                                  blank=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    location_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} | {self.company.name}'

    class Meta:
        db_table = 'ice_cream_truck'
        verbose_name_plural = 'Ice Cream Truck'


class Customers(AbstractUUID):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    ice_cream_truck = models.ForeignKey(IceCreamTruck, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} | {self.ice_cream_truck.name}'

    class Meta:
        db_table = 'customer'
        verbose_name_plural = 'Customers'
