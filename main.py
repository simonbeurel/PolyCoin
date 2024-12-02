"""
A simple Blockchain in Python
"""

import hashlib
from flask import Flask, jsonify, request
import datetime

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption,
    load_pem_private_key, load_pem_public_key
)

class PolyCoinBlock:
    def __init__(self, previous_block_hash, source_code, signature):
        self.type = "CODE"
        self.previous_block_hash = previous_block_hash
        self.source_code = source_code
        self.timestamp = datetime.datetime.now()

        self.signature = signature

        self.block_data = f"{source_code} - {previous_block_hash} - {self.timestamp}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()

    def to_dict(self):
        """Convert the block's data into a dictionary."""
        return {
            'type': self.type,
            'previous_block_hash': self.previous_block_hash,
            'source_code': self.source_code,
            'timestamp': str(self.timestamp),
            'block_hash': self.block_hash,
            'signature': self.signature
        }

    def verify_block(self, public_key_pem: str) -> bool:
        code_encode = self.source_code.encode('utf-8')
        loaded_public_key = load_pem_public_key(public_key_pem)
        try:
            loaded_public_key.verify(
                self.signature,
                code_encode,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            print("\nLa signature est valide.")
            return True
        except Exception as e:
            print("\nLa signature est invalide :", str(e))
            return False


class PolyCoinBlockIdentifier:
    def __init__(self, previous_block_hash, name_organization, public_key_pem, certificate):
        self.type = "IDENTIFIER"
        self.name_organization = name_organization
        self.public_key_pem = public_key_pem
        self.certificate = certificate

        self.timestamp = datetime.datetime.now()
        self.block_data = f"{name_organization} - {previous_block_hash} - {self.timestamp}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()

        self.previous_block_hash = previous_block_hash
    
    def to_dict(self):
        """Convert the block's data into a dictionary."""
        return {
            'type': self.type,
            'previous_block_hash': self.previous_block_hash,
            'timestamp': str(self.timestamp),
            'block_hash': self.block_hash,
            'name_organization': self.name_organization,
            'public_key_pem': self.public_key_pem.decode('utf-8')
        }


class Blockchain:
    def __init__(self):
        self.chain = []
        self.generate_genesis_block()
        self.dic_pub_key = {}

    def generate_genesis_block(self):
        self.chain.append(PolyCoinBlock("0", "Genesis Block made by Simon Beurel", None))

    def create_block_from_source_code(self, source_code, signature):
        previous_block_hash = self.last_block.block_hash
        self.chain.append(PolyCoinBlock(previous_block_hash, source_code, signature))
    
    def create_block_from_identifier(self, name_organization, public_key_pem, certificate):
        previous_block_hash = self.last_block.block_hash
        self.chain.append(PolyCoinBlockIdentifier(previous_block_hash, name_organization, public_key_pem, certificate))

    def store_public_key(self, name_organization, public_key) -> bool:
        if name_organization not in self.dic_pub_key:
            self.dic_pub_key[name_organization] = public_key
            print(f"Public key added for {name_organization}")
            return True
        else:
            print(f"Public key for {name_organization} already exist.")
            return False

    @property
    def last_block(self):
        return self.chain[-1]


app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine_block_code', methods=['GET'])
def mine_block():
    source_code = request.args.get('source_code')
    signature = request.args.get('signature')
    if not source_code:
        return jsonify({'error': 'Missing source_code parameter'}), 400
    elif not signature:
        return jsonify({'error': 'Missing signature parameter'}), 400

    blockchain.create_block_from_source_code(source_code, signature)  
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

@app.route('/mine_block_identifier', methods=['GET'])
def mine_block_identifier():
    name_organization = request.args.get('name_organization')
    certificate = request.args.get('certificate')

    if not name_organization:
        return jsonify({'error': 'Missing name_organization parameter'}), 400
    elif not certificate:
        return jsonify({'error': 'Missing certificate parameter'}), 400

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    if blockchain.store_public_key(name_organization, public_key):

        public_key_pem = public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )

        blockchain.create_block_from_identifier(name_organization, public_key_pem, certificate)

        last_block = blockchain.last_block
        response = {
            'block_hash': last_block.block_hash,
            'previous_block_hash': last_block.previous_block_hash,
            'timestamp': str(last_block.timestamp)
        }
        return jsonify(response), 200
    
    else:
        return jsonify({'error': 'Organization already registered'}), 400






app.run(host='127.0.0.1', port=5000)