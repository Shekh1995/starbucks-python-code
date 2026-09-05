import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_homepage():
    res = client.get(/)
    assert res.status_code == 200
    assert Handcrafted Curations in res.text
    assert Barista Recommends in res.text

def test_ordering_page():
    res = client.get(/ordering)
    assert res.status_code == 200
    assert Starbucks Order Menu in res.text
    assert Caffe Latte in res.text

def test_giftcards_page():
    res = client.get(/giftcards)
    assert res.status_code == 200
    assert Starbucks e-Gift Cards in res.text

def test_pay_page():
    res = client.get(/pay)
    assert res.status_code == 200
    assert Starbucks Pay & Card in res.text

def test_store_page():
    res = client.get(/store)
    assert res.status_code == 200
    assert Connaught Place in res.text

def test_search():
    res = client.get(/search?q=latte)
    assert res.status_code == 200
    assert Caffe Latte in res.text

def test_api_cart_flow():
    # Clear cart first
    res_clear = client.post(/api/cart/clear)
    assert res_clear.status_code == 200
    
    # Add item
    res_add = client.post(/api/cart/add, json={item_id: br-1, quantity: 2})
    assert res_add.status_code == 200
    data = res_add.json()
    assert data[status] == success
    assert data[count] == 2

    # Get cart
    res_cart = client.get(/api/cart)
    assert res_cart.status_code == 200
    assert res_cart.json()[count] == 2
