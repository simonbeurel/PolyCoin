"""
A simple Blockchain in Python
"""

import hashlib
from flask import Flask, jsonify, request
import datetime

class PolyCoinBlock:
    def __init__(self, previous_block_hash, source_code: str):
        self.previous_block_hash = previous_block_hash
        self.source_code = source_code
        self.timestamp = datetime.datetime.now()

        self.block_data = f"{source_code} - {previous_block_hash} - {self.timestamp}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()

    def to_dict(self):
        """Convert the block's data into a dictionary."""
        return {
            'previous_block_hash': self.previous_block_hash,
            'source_code': self.source_code,
            'timestamp': str(self.timestamp),
            'block_hash': self.block_hash
        }


class Blockchain:
    def __init__(self):
        self.chain = []
        self.generate_genesis_block()

    def generate_genesis_block(self):
        self.chain.append(PolyCoinBlock("0", "Genesis Block made by Simon Beurel"))

    def create_block_from_source_code(self, source_code):
        previous_block_hash = self.last_block.block_hash
        self.chain.append(PolyCoinBlock(previous_block_hash, source_code))

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

    blockchain.create_block_from_source_code(source_code)
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


app.run(host='127.0.0.1', port=5000)
