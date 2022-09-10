import pytest
from django.contrib.auth.models import Group

from faker import Faker

from apps.core.models import Company, User
from apps.utils.enums import UserTypeEnum
from rest_framework.test import APIClient

fake = Faker()


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
@pytest.fixture
def setup_user_company():
    user_info = dict(
        name='John Test',
        email='johndoe@gmail.com',
        user_type=UserTypeEnum.COMPANY_OWNER,
        mobile='09023123221'
    )
    group, _ = Group.objects.get_or_create(name="company")
    company_info = dict(
        name='John AB',
        user=None
    )
    instance = User.objects.create_user(username='john_test',
                                        password='john_test', **user_info)
    company_info.update({'user': instance})
    _ = Company.objects.create(**company_info)
    instance.groups.add(group)
    instance.save()
    user_info.update({
        'username': 'john_test',
        'password': 'john_test'
    })
    return instance, user_info


@pytest.fixture
def auth_client(client, setup_user_company):
    user, user_info = setup_user_company
    response = client.post('/api/v1/token/',
                           dict(username=user_info.get('username'), password=user_info.get('password')))
    data = response.data
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + data.get('access'))
    return client


@pytest.fixture
def setup_franchise(auth_client):
    payload = {
        "name": "Franchise AB",
        "description": fake.sentence(),
        "manager_info": {
            "name": fake.name(),
            "email": "manager@gmail.com",
            "password": "manager_test"
        }
    }
    response = auth_client.post('/api/v1/franchise/', payload, format='json')
    assert response.status_code == 201
    return payload


@pytest.fixture
def franchise_client(client, setup_franchise):
    user_info = setup_franchise
    response = client.post('/api/v1/token/',
                           dict(username=user_info["manager_info"]["email"],
                                password=user_info["manager_info"]["password"]))
    data = response.data
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + data.get('access'))
    return client


@pytest.fixture
def setup_truck(auth_client, setup_user_company):
    payload = {
        "name": fake.name(),
        "country": fake.country(),
        "state": fake.city(),
        "location_name": fake.address(),
    }
    response = auth_client.post('/api/v1/ice-cream-truck/', payload)
    assert response.status_code == 201
    resp = auth_client.get('/api/v1/ice-cream-truck/')
    result = resp.data['data']['results']
    return result


@pytest.fixture
def setup_flavor(auth_client, setup_truck):
    results = setup_truck
    payload = [
        {
            "name": 'Chocolate',
            "ice_cream_truck": results[0]['id']
        },
        {
            "name": 'Pistachio',
            "ice_cream_truck": results[0]['id']
        },
        {
            "name": 'Strawberry',
            "ice_cream_truck": results[0]['id']
        },
        {
            "name": 'Mint',
            "ice_cream_truck": results[0]['id']
        },
    ]
    for load in payload:
        resp = auth_client.post('/api/v1/store/flavor/', load)
        assert resp.status_code == 201

    response = auth_client.get('/api/v1/store/flavor/')
    assert response.status_code == 200
    results = response.data['results']
    assert len(results) == 4
    return results


@pytest.fixture
def setup_customer(auth_client, setup_truck):
    payload = {
        "name": fake.name(),
        "email": fake.email()
    }
    resp = auth_client.get('/api/v1/ice-cream-truck/')
    data = resp.data
    result = data['data']['results'][0]
    response = auth_client.post(f'/api/v1/ice-cream-truck/{result["id"]}/add_customer/', payload)
    assert response.status_code == 201
    return response.data['data']


@pytest.fixture
def setup_store(auth_client, setup_user_company, setup_truck, setup_flavor):
    trucks = setup_truck
    flavors = setup_flavor
    payload = [
        {
            "name": "Shaved ice",
            "qty": 10,
            "description": fake.sentence(),
            "price": 1000,
            "flavor": flavors[0]['id'],
            "ice_cream_truck": trucks[0]['id']
        },
        {
            "name": "Chocolate bars",
            "qty": 10,
            "description": fake.sentence(),
            "price": 1000,
            "flavor": flavors[1]['id'],
            "ice_cream_truck": trucks[0]['id']
        },
        {
            "name": "Ice creams",
            "qty": 3,
            "description": fake.sentence(),
            "price": 200,
            "flavor": flavors[2]['id'],
            "ice_cream_truck": trucks[0]['id']
        },
    ]
    for load in payload:
        response = auth_client.post('/api/v1/store/store/', load)
        assert response.status_code == 201
    # get all ice creams by truck
    response = auth_client.get(f'/api/v1/store/store/?ice_cream_truck_id={trucks[0]["id"]}')
    assert response.status_code == 200
    results = response.data['data']['results']
    assert len(results) == 3
    return results


@pytest.fixture
def setup_order(auth_client, setup_customer, setup_store):
    customer = setup_customer
    stores = setup_store
    payload = [
        {
            "customer": customer['id'],
            "ice_cream_truck": stores[0]['ice_cream_truck']['id'],
            "item": stores[0]['id'],
            "qty": 2
        },
        {
            "customer": customer['id'],
            "ice_cream_truck": stores[1]['ice_cream_truck']['id'],
            "item": stores[1]['id'],
            "qty": 5
        },
        {
            "customer": customer['id'],
            "ice_cream_truck": stores[2]['ice_cream_truck']['id'],
            "item": stores[2]['id'],
            "qty": 3
        },
    ]
    for load in payload:
        response = auth_client.post('/api/v1/order/', load)
        print(response.data)
        assert response.status_code == 201
    response = auth_client.get('/api/v1/order/')
    results = response.data['data']['results']
    return results
