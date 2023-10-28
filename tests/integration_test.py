import sys
import pytest

sys.path.append('../app/')
from server import app

@pytest.fixture()
def test_client():
    client = app.test_client()
    return client

def test_category_api_1(test_client):
    response = test_client.get('/api/v1/category/愛情')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert 'dramas' in data

def test_category_api_2(test_client):
    response = test_client.get('/api/v1/category/愛情劇')
    assert response.status_code == 404

def test_search_api(test_client):
    response = test_client.get('/api/v1/search/漢江')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert 'dramas' in data

def test_keyword_api(test_client):
    response = test_client.get('/api/v1/search/漢江人')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert data == '{"dramas": []}'

    