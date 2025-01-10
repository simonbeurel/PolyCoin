import pytest
import requests
import subprocess
import time
import rsa
import base64

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="session")
def start_server():
    server = subprocess.Popen(["python3", "app.py"])
    time.sleep(3)  # Temps pour s'assurer que le serveur démarre
    yield
    server.terminate()
    server.wait()

def test_mine_block_code(start_server):
    response = requests.get(f"{BASE_URL}/mine_block_code", params={
        "source_code": "print('Hello, Blockchain!')",
        "signature": "dummy_signature"
    })
    assert response.status_code == 200


def test_mine_block_identifier(start_server):
    public_key, private_key = rsa.newkeys(2048)
    public_key_str = public_key.save_pkcs1().decode('utf-8')
    response = requests.get(f"{BASE_URL}/mine_block_identifier", params={
        "name_organization": "TestOrg",
        "certificate": "dummy_certificate",
        "walletETH": "0x1234567890abcdef",
        "public_key_str": public_key_str
    })
    assert response.status_code == 200


def test_get_chain(start_server):
    response = requests.get(f"{BASE_URL}/get_chain")
    assert response.status_code == 200

def test_e2e_final(start_server):
    assert 1 == 1

    #Etape1: On génère la paire de clé et on l'envoie sur la blockchain
    public_key, private_key = rsa.newkeys(2048)
    public_key_str = public_key.save_pkcs1().decode('utf-8')
    #public_key_restored = rsa.PublicKey.load_pkcs1(public_key_str.encode('utf-8'))
    response = requests.get(f"{BASE_URL}/mine_block_identifier", params={
        "name_organization": "TestOrg2",
        "certificate": "dummy_certificate",
        "walletETH": "0x1234567890abczef",
        "public_key_str": public_key_str
    })

    #Etape2: On signe notre code et on l'envoie
    source_code = "from ethereum import ..."
    signature = rsa.sign(source_code.encode('utf-8'), private_key, 'SHA-256')
    signature_base64 = base64.b64encode(signature).decode('utf-8')
    response = requests.get(f"{BASE_URL}/mine_block_code", params={
        "source_code": source_code,
        "signature": signature_base64
    })
    assert response.status_code == 200
    block_hash = response.json()['block_hash']
    print('Block hash :', block_hash)


    #Etape3: Vérifier la signature
    response = requests.get(f"{BASE_URL}/verify_block_signature", params={
        "block_hash": block_hash
    })
    assert response.status_code == 200
    print(response.json())

    '''
    try:
        rsa.verify(source_code.encode('utf-8'), signature, public_key)
        print("La signature est valide.")
    except rsa.VerificationError:
        print("La signature est invalide.")
    '''


#TODO: coté serveur -> recupérer la signature et la décodé, récupérer la public key et la décodé, faire la vérification de signature







    
