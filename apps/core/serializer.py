from rest_framework import serializers
from django.contrib.auth.models import Group
from apps.core.models import User, Company, Franchise, IceCreamTruck, Customers
from apps.utils.enums import UserTypeEnum


class UserSerializer(serializers.ModelSerializer):
    """
    This class handles serializer handles serializing of user model
    """

    class Meta:
        model = User
        fields = ['id', 'name', 'email']


class UserRegisterSerializer(serializers.Serializer):
    """
    this class handles user with his / her company registration validation ,creation
    """
    name = serializers.CharField(max_length=255, required=True)
    company_name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(max_length=255, required=True)
    mobile = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(max_length=255, required=True, min_length=8)

    def validate(self, attrs):
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({'email': 'Email already exist inside our system'})
        if attrs.get('mobile'):
            if User.objects.filter(mobile=attrs.get('mobile')).exists():
                raise serializers.ValidationError({'mobile': 'Mobile already exist inside our system'})
        return attrs

    def create(self, validated_data):
        user_info = {
            'name': validated_data.get('name'),
            'email': validated_data.get('email'),
            'mobile': validated_data.get('mobile'),
            'user_type': UserTypeEnum.COMPANY_OWNER
        }
        group, _ = Group.objects.get_or_create(name="company")
        company_info = {
            'name': validated_data.get('company_name'),
            'user': None
        }
        instance = User.objects.create_user(username=validated_data.get('username'),
                                            password=validated_data.get('password'), **user_info)
        company_info.update({'user': instance})
        _ = self.create_company(company_info)
        instance.groups.add(group)
        instance.save()
        return instance

    @staticmethod
    def create_company(company_payload):
        company = Company.objects.create(**company_payload)
        return company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = '__all__'


class CustomerFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(max_length=255, required=True)

    def create(self, validated_data):
        instance = Customers.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        pass


class FranchiseSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Franchise
        fields = ['id', 'company', 'name', 'description']


class ManagerFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True, min_length=8)

    def validate(self, attrs):
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({'email': 'Email already exist inside our system'})
        if attrs.get('mobile'):
            if User.objects.filter(mobile=attrs.get('mobile')).exists():
                raise serializers.ValidationError({'mobile': 'Mobile already exist inside our system'})
        return attrs

    def create(self, validated_data):
        validated_data.update({'user_type': UserTypeEnum.FRANCHISE})
        group, _ = Group.objects.get_or_create(name="franchise")
        instance = User.objects.create_user(username=validated_data.pop('username'),
                                            password=validated_data.pop('password'), **validated_data)
        instance.groups.add(group)
        return instance

    def update(self, instance, validated_data):
        pass


class FranchiseFormSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    manager_info = ManagerFormSerializer(required=False)

    def create(self, validated_data):
        franchise = Franchise.objects.create(**validated_data)
        return franchise

    def update(self, instance, validated_data):
        _ = Franchise.objects.filter(id=instance.id).update(**validated_data)
        return instance


class IceCreamTruckSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    franchise = FranchiseSerializer(read_only=True)

    class Meta:
        model = IceCreamTruck
        fields = ['id', 'company', 'franchise', 'name', 'country', 'state', 'location_name']


class IceCreamTruckFormSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    location_name = serializers.CharField(required=True)

    def create(self, validated_data):
        instance = IceCreamTruck.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        pass
