import pytest
from faker import Faker

fake = Faker()


@pytest.mark.django_db
class TestStore:
    def test_create_store_entry(self, setup_truck, auth_client, setup_flavor):
        trucks = setup_truck
        flavors = setup_flavor
        payload = {
            "name": "Shaved ice",
            "qty": 10,
            "description": fake.sentence(),
            "price": 1000,
            "flavor": flavors[0]['id'],
            "ice_cream_truck": trucks[0]['id']
        }
        response = auth_client.post('/api/v1/store/store/', payload)
        assert response.status_code == 201
        data = response.data['data']
        assert payload['name'] == data['name']
        assert payload['qty'] == data['qty']
        assert payload['price'] == data['price']
        assert payload['flavor'] == data['flavor']['id']

    def test_update_store_entry(self, auth_client, setup_store):
        stores = setup_store
        payload = {
            "name": "Shaved ice",
            "qty": 8,
            "description": fake.sentence(),
            "price": 1000,
            "flavor": stores[0]['flavor']['id'],
            "ice_cream_truck": stores[0]['ice_cream_truck']['id']
        }
        response = auth_client.put(f'/api/v1/store/store/{stores[0]["id"]}/', payload)
        assert response.status_code == 200
        data = response.data['data']
        assert data['qty'] == payload['qty']

    def test_add_new_stock_to_store(self, auth_client, setup_store):
        stores = setup_store
        store = stores[0]
        current_qty = store['qty']
        added_stock = 20
        response = auth_client.put(f'/api/v1/store/store/{store["id"]}/stock/', {
            "qty": added_stock
        })
        assert response.status_code == 200
        response = auth_client.get(f'/api/v1/store/store/{store["id"]}/')
        assert response.status_code == 200
        data = response.data
        assert data['qty'] == (current_qty + added_stock)

    def test_get_truck_inventory(self, auth_client, setup_truck, setup_store):
        truck = setup_truck
        response = auth_client.get(f'/api/v1/store/store/?ice_cream_truck_id={truck[0]["id"]}')
        assert response.status_code == 200
        results = response.data['data']['results']
        assert len(results) == 3
