import pytest


@pytest.mark.django_db
class TestOrder:
    def test_create_order(self, auth_client, setup_customer, setup_store):
        """
        method to test successful ice cream order
        """
        customer = setup_customer
        stores = setup_store
        payload = {
            "customer": customer['id'],
            "ice_cream_truck": stores[0]['ice_cream_truck']['id'],
            "item": stores[0]['id'],
            "qty": 2
        }
        response = auth_client.post('/api/v1/order/', payload)
        assert response.status_code == 201
        data = response.data
        assert 'ENJOY!' in data.get('message')

    def test_create_order_fail(self, auth_client, setup_customer, setup_store):
        """
            method to test unsuccessful ice cream order
        """
        customer = setup_customer
        stores = setup_store
        payload = {
            "customer": customer['id'],
            "ice_cream_truck": stores[0]['ice_cream_truck']['id'],
            "item": stores[0]['id'],
            "qty": 20
        }
        response = auth_client.post('/api/v1/order/', payload)
        assert response.status_code == 400
        data = response.data
        assert "SORRY!" in data.get('message')
