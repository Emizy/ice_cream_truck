import pytest
from faker import Faker
from rest_framework.test import APIClient

fake = Faker()


@pytest.mark.django_db
class TestFranchise:

    def test_create_franchise(self, auth_client):
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
        data = response.data
        assert payload.get('name') == data['data']['name']
        assert payload.get('description') == data['data']['description']

    def test_create_franchise_permission_for_non_company(self, auth_client):
        payload = {
            "name": "Franchise AB 01",
            "description": fake.sentence(),
            "manager_info": {
                "name": fake.name(),
                "email": "manager_ab@gmail.com",
                "password": "manager_test"
            }
        }
        response = auth_client.post('/api/v1/franchise/', payload, format='json')

        # login manager in
        client = APIClient()
        manager_response = client.post('/api/v1/token/', {'username': payload['manager_info']['email'],
                                                          'password': payload['manager_info']['password']})
        data = manager_response.data
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + data.get('access'))
        response = client.post('/api/v1/franchise/', payload, format='json')
        assert response.status_code == 403

    def test_get_all_franchise(self, auth_client, setup_franchise):
        response = auth_client.get('/api/v1/franchise/')
        assert response.status_code == 200
        data = response.data
        assert len(data['data']['results']) > 0

    def test_update_franchise(self, auth_client, setup_franchise):
        payload = {
            "name": "Franchise ABs",
            "description": fake.sentence(),
        }
        response = auth_client.get('/api/v1/franchise/')
        data = response.data
        result = data['data']['results'][0]
        response_ = auth_client.put(f'/api/v1/franchise/{result["id"]}/', payload)
        assert response.status_code == 200
        data_ = response_.data
        assert payload['name'] == data_['data']['name']
        assert payload['description'] == data_['data']['description']

    def test_get_franchise(self, auth_client, setup_franchise):
        response = auth_client.get('/api/v1/franchise/')
        data = response.data
        result = data['data']['results'][0]
        response_ = auth_client.get(f'/api/v1/franchise/{result["id"]}/')
        data_ = response_.data
        assert result == data_.get('data')

    def test_delete_franchise(self, auth_client, setup_franchise):
        response = auth_client.get('/api/v1/franchise/')
        data = response.data
        result = data['data']['results'][0]
        response_ = auth_client.delete(f'/api/v1/franchise/{result["id"]}/')
        assert response_.status_code == 204
        response_ = auth_client.get(f'/api/v1/franchise/{result["id"]}/')
        assert response_.status_code == 400
