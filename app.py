from flask import Flask, jsonify, request
from blockchain.blockchain import Blockchain
from config.keys import generate_keys

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
    if not name_organization or not certificate or not walletETH:
        return jsonify({'error': 'Missing parameters'}), 400

    private_key_pem, public_key_pem = generate_keys()
    if blockchain.store_public_key(name_organization, public_key_pem):
        blockchain.create_block_from_identifier(name_organization, public_key_pem, certificate, walletETH)
        last_block = blockchain.last_block
        response = last_block.to_dict()
        response['private_key'] = private_key_pem.decode('utf-8')
        return jsonify(response), 200
    return jsonify({'error': 'Organization already exists'}), 400

@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain_data = [block.to_dict() for block in blockchain.chain]
    return jsonify({'chain': chain_data, 'length': len(chain_data)}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
