"""
A simple Blockchain in Python
"""

import hashlib
from flask import Flask, jsonify, request
import datetime

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)

class PolyCoinBlock:
    def __init__(self, previous_block_hash, source_code: str, hashed_code, signature):
        self.previous_block_hash = previous_block_hash
        self.source_code = source_code
        self.timestamp = datetime.datetime.now()

        self.hashed_code = hashed_code
        self.signed_message = signature

        self.block_data = f"{source_code} - {previous_block_hash} - {self.timestamp}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()

    def to_dict(self):
        """Convert the block's data into a dictionary."""
        return {
            'previous_block_hash': self.previous_block_hash,
            'source_code': self.source_code,
            'timestamp': str(self.timestamp),
            'block_hash': self.block_hash,
            'signed_message': self.signed_message
        }

    def verify_block(self, public_key_pem: str) -> bool:
        try:
            public_key = load_pem_public_key(public_key_pem.encode())
            computed_hash = hashlib.sha256(self.source_code.encode()).digest()  # Utiliser digest()

            if computed_hash != self.hashed_code:
                print("Mismatch between the computed hash and provided hash.")
                return False

            public_key.verify(
                self.signed_message,
                computed_hash,  # Correct format
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Verification failed: {e}")
            return False



class Blockchain:
    def __init__(self):
        self.chain = []
        self.generate_genesis_block()

    def generate_genesis_block(self):
        self.chain.append(PolyCoinBlock("0", "Genesis Block made by Simon Beurel", None, None))

    def create_block_from_source_code(self, source_code, hashed_code, signature):
        previous_block_hash = self.last_block.block_hash
        self.chain.append(PolyCoinBlock(previous_block_hash, source_code, signed_message, hashed_code))

    @property
    def last_block(self):
        return self.chain[-1]


app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    source_code = request.args.get('source_code')
    if not source_code:
        return jsonify({'error': 'Missing source_code parameter'}), 400

    blockchain.create_block_from_source_code(source_code, None, None) 
    #TODO: CHANGER PAR LA SUITE PAR LES VRAIES VALEURS 
    last_block = blockchain.last_block

    response = {
        'block_hash': last_block.block_hash,
        'previous_block_hash': last_block.previous_block_hash,
        'timestamp': str(last_block.timestamp)
    }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def display_chain():
    # Use the `to_dict` method to convert each block into a dictionary
    chain_data = [block.to_dict() for block in blockchain.chain]
    response = {
        'chain': chain_data,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


#app.run(host='127.0.0.1', port=5000)



'''TEST SIGNATURE'''
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

private_key_pem = private_key.private_bytes(
    encoding=Encoding.PEM,
    format=PrivateFormat.PKCS8,
    encryption_algorithm=NoEncryption()
)

public_key_pem = public_key.public_bytes(
    encoding=Encoding.PEM,
    format=PublicFormat.SubjectPublicKeyInfo
)

code = b"test"
signature = private_key.sign(
    code,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

try:
    public_key.verify(
        signature,
        code,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("\nLa signature est valide.")
except Exception as e:
    print("\nLa signature est invalide :", str(e))