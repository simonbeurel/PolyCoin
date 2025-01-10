from flask import Flask, jsonify, request
from blockchain.blockchain import Blockchain
from config.keys import generate_keys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)

import rsa
import base64

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine_block_code', methods=['GET'])
def mine_block_code():
    source_code = request.args.get('source_code')
    signature = request.args.get('signature')
    if not source_code or not signature:
        return jsonify({'error': 'Missing parameters'}), 400
    blockchain.create_block_from_source_code(source_code, signature)
    last_block = blockchain.last_block
    return jsonify(last_block.to_dict()), 200

@app.route('/mine_block_identifier', methods=['GET'])
def mine_block_identifier():
    name_organization = request.args.get('name_organization')
    certificate = request.args.get('certificate')
    walletETH = request.args.get('walletETH')
    public_key_str = request.args.get('public_key_str')
    if not name_organization or not certificate or not walletETH or not public_key_str:
        return jsonify({'error': 'Missing parameters'}), 400

    if blockchain.store_public_key(name_organization, public_key_str):
        blockchain.create_block_from_identifier(name_organization, public_key_str, certificate, walletETH)
        last_block = blockchain.last_block
        response = last_block.to_dict()
        return jsonify(response), 200
    return jsonify({'error': 'Organization already exists'}), 400

@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain_data = [block.to_dict() for block in blockchain.chain]
    return jsonify({'chain': chain_data, 'length': len(chain_data)}), 200


@app.route('/verify_block_signature', methods=['GET'])
def verify_block_signature():
    block_hash = request.args.get('block_hash')

    source_code = ''
    signature = ''

    for block in blockchain.chain:
        if block.type == "CODE" and block.block_hash == block_hash:
            signature = block.signature
            source_code = block.source_code
    
    signature_decoded = base64.b64decode(signature.encode('utf-8'))
    code_source_decoded = source_code.encode('utf-8')

    for name_org,pub_key in blockchain.dic_pub_key.items():
        pub_key_restored = rsa.PublicKey.load_pkcs1(pub_key.encode('utf-8'))

        try:
            rsa.verify(code_source_decoded, signature_decoded, pub_key_restored)
            print("La signature est valide.")
            return jsonify({'name_org': name_org}), 200
        except rsa.VerificationError:
            print("La signature est invalide.")

    return jsonify({'error': 'No organizations found'}), 400






if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
