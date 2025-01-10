import pytest
import requests
import subprocess
import time

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="session")
def start_server():
    server = subprocess.Popen(["python3", "app.py"])
    time.sleep(3)  # Temps pour s'assurer que le serveur démarre
    yield

def test_mine_block_code(start_server):
    response = requests.get(f"{BASE_URL}/mine_block_code", params={
        "source_code": "print('Hello, Blockchain!')",
        "signature": "dummy_signature"
    })
    assert response.status_code == 200


def test_mine_block_identifier(start_server):
    response = requests.get(f"{BASE_URL}/mine_block_identifier", params={
        "name_organization": "TestOrg",
        "certificate": "dummy_certificate",
        "walletETH": "0x1234567890abcdef"
    })
    assert response.status_code == 200


def test_get_chain(start_server):
    response = requests.get(f"{BASE_URL}/get_chain")
    assert response.status_code == 200


    
