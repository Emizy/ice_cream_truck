import pytest
from django.db.models import Sum
from faker import Faker
from apps.orders.models import Order
from apps.core.models import Customers

fake = Faker()


@pytest.mark.django_db
class TestTruck:
    def test_create_company_truck(self, auth_client):
        payload = {
            "name": fake.name(),
            "country": fake.country(),
            "state": fake.city(),
            "location_name": fake.address(),
        }
        response = auth_client.post('/api/v1/ice-cream-truck/', payload)
        assert response.status_code == 201
        data = response.data['data']
        assert data.get('name') == payload['name']
        assert data.get('country') == payload['country']
        assert data.get('state') == payload['state']
        assert data.get('location_name') == payload['location_name']

    def test_create_franchise_truck(self, franchise_client):
        payload = {
            "name": fake.name(),
            "country": fake.country(),
            "state": fake.city(),
            "location_name": fake.address(),
        }
        response = franchise_client.post('/api/v1/ice-cream-truck/', payload)
        assert response.status_code == 201
        data = response.data['data']
        assert data.get('name') == payload['name']
        assert data.get('country') == payload['country']
        assert data.get('state') == payload['state']
        assert data.get('location_name') == payload['location_name']

    def test_create_customer(self, auth_client, setup_truck):
        payload = {
            "name": fake.name(),
            "email": fake.email()
        }
        resp = auth_client.get('/api/v1/ice-cream-truck/')
        data = resp.data
        result = data['data']['results'][0]
        response = auth_client.post(f'/api/v1/ice-cream-truck/{result["id"]}/add_customer/', payload)
        assert response.status_code == 201
        result = response.data
        assert payload['name'] == result['data']['name']
        assert payload['email'] == result['data']['email']

    def test_ice_truck_kpi(self, auth_client, setup_order):
        resp = auth_client.get('/api/v1/ice-cream-truck/')
        data = resp.data
        result = data['data']['results'][0]
        response = auth_client.get(f'/api/v1/ice-cream-truck/{result["id"]}/kpi/')
        assert response.status_code == 200
        data = response.data
        assert 'total_amount' in data
        assert 'customers' in data
        total_truck_sales = Order.objects.filter(ice_cream_truck_id=result["id"]).aggregate(
            total_amount=Sum('total_price'))
        customers = Customers.objects.filter(ice_cream_truck_id=result["id"])
        amount = total_truck_sales['total_amount'] if total_truck_sales['total_amount'] is not None else 0
        assert amount == data.get('total_amount')
        assert customers.count() == data.get('customers')
