import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_display_chain(client):
    response = client.get('/get_chain')
    assert response.status_code == 200
    data = response.get_json()
    assert 'chain' in data
    assert 'length' in data

def test_mine_block(client):
    response = client.get('/mine_block_code', query_string={
        'source_code': 'test code',
        'signature': 'test signature'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'block_hash' in data
    assert 'timestamp' in data
