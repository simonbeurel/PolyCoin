"""
A simple Blockchain in Python
"""

import hashlib

class PolyCoinBlock:
    
    def __init__(self, previous_block_hash, source_code:str):

        self.previous_block_hash = previous_block_hash
        self.source_code = source_code

        self.block_data = f"{source_code} - {previous_block_hash}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.generate_genesis_block()

    def generate_genesis_block(self):
        self.chain.append(PolyCoinBlock("0", "Genesis Block made by Simon Beurel"))
    
    def create_block_from_source_code(self, source_code):
        previous_block_hash = self.last_block.block_hash
        self.chain.append(PolyCoinBlock(previous_block_hash, source_code))

    def display_chain(self):
        for i in range(len(self.chain)):
            print(f"Data {i + 1}: {self.chain[i].block_data}")
            print(f"Hash {i + 1}: {self.chain[i].block_hash}\n")

    @property
    def last_block(self):
        return self.chain[-1]


t1 = "import library from .... return '0'"
t2 = "^pragma solidity version.... public view returns(uint256)...."
t3 = "#include <stdio> ...."

myblockchain = Blockchain()

myblockchain.create_block_from_source_code(t1)
myblockchain.create_block_from_source_code(t2)
myblockchain.create_block_from_source_code(t3)

myblockchain.display_chain()