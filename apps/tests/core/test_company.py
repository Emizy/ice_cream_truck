import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_company(client):
    payload = dict(
        name="John Doc",
        company_name="John Doe AB",
        email="johndoe@gmail.com",
        mobile="08139572200",
        password="$rootpa$$"
    )
    response = client.post('/api/v1/register/', payload)
    assert response.status_code == 201
    data = response.data
    assert data.get('message') == 'Account created successfully'


@pytest.mark.django_db
def test_login_company(setup_user_company, client):
    user, user_info = setup_user_company
    response = client.post('/api/v1/token/',
                           dict(username=user_info.get('username'), password=user_info.get('password')))
    assert response.status_code == 200
    data = response.data
    assert 'access' in data


@pytest.mark.django_db
def test_login_company_fail(client):
    response = client.post('/api/v1/token/', dict(username='johndoe@gmail.com', password='rootpa$$'))
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_me(auth_client, setup_user_company):
    user, user_info = setup_user_company
    response = auth_client.get('/api/v1/user/me/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_user_company(auth_client, setup_user_company):
    user, _ = setup_user_company
    response = auth_client.get('/api/v1/company/')
    assert response.status_code == 200
    data = response.data
    assert len(data['data']['results']) > 0
    company = data['data']['results'][0]
    assert user.id == company.get('user')
