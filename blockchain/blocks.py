import hashlib
import datetime
from typing import List

from .merkle_tree import MerkleTree



class PolyCoinBlock:
    def __init__(self, previous_block_hash, source_code, signature):
        self.type = "CODE"
        self.previous_block_hash = previous_block_hash
        self.source_code = source_code
        self.timestamp = datetime.datetime.now()
        self.signature = signature

        # Create transactions list from block data
        self.transactions = [
            f"source_code:{source_code}",
            f"previous_hash:{previous_block_hash}",
            f"timestamp:{self.timestamp}",
            f"signature:{signature}"
        ]

        # Build Merkle tree
        self.merkle_tree = MerkleTree.build_tree(self.transactions)
        self.merkle_root = self.merkle_tree.hash if self.merkle_tree else None

        self.block_data = f"{source_code} - {previous_block_hash} - {self.timestamp} - {self.merkle_root}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()

    def to_dict(self):
        return {
            'type': self.type,
            'previous_block_hash': self.previous_block_hash,
            'source_code': self.source_code,
            'timestamp': str(self.timestamp),
            'block_hash': self.block_hash,
            'signature': self.signature,
            'merkle_root': self.merkle_root,
            'transactions': self.transactions
        }

    def get_merkle_proof(self, tx: str) -> List[tuple[str, bool]]:
        """
        Generate a Merkle proof for a given transaction hash.
        Returns a list of (hash, is_left) tuples representing the proof path.
        """
        proof = []
        if not self.merkle_tree:
            return proof

        tx_hash = MerkleTree.hash_data(tx)
        proof, found = MerkleTree.get_proof(self.merkle_tree, tx_hash)
        return proof

class PolyCoinBlockIdentifier:
    def __init__(self, previous_block_hash, name_organization, public_key_str, certificate, wallet_eth_address):
        self.type = "IDENTIFIER"
        self.name_organization = name_organization
        self.public_key_str = public_key_str
        self.certificate = certificate
        self.walletETH = wallet_eth_address
        self.timestamp = datetime.datetime.now()

        self.transactions = [
            f"name:{name_organization}",
            f"previous_hash:{previous_block_hash}",
            f"timestamp:{self.timestamp}",
            f"certificate:{certificate}",
            f"wallet:{wallet_eth_address}"
        ]
        self.merkle_tree = MerkleTree.build_tree(self.transactions)
        self.merkle_root = self.merkle_tree.hash if self.merkle_tree else None

        self.block_data = f"{name_organization} - {previous_block_hash} - {self.timestamp} - {self.merkle_root}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()
        self.previous_block_hash = previous_block_hash

    def to_dict(self):
        return {
            'type': self.type,
            'previous_block_hash': self.previous_block_hash,
            'timestamp': str(self.timestamp),
            'block_hash': self.block_hash,
            'name_organization': self.name_organization,
            'public_key_str': self.public_key_str,
            'wallet_eth_address': self.walletETH,
            "merkle_root": self.merkle_root,
            "transactions": self.transactions
        }

    def get_merkle_proof(self, tx: str) -> List[tuple[str, bool]]:
        """
        Generate a Merkle proof for a given transaction.
        """
        if not self.merkle_tree:
            return []

        tx_hash = MerkleTree.hash_data(tx)
        proof, found = MerkleTree.get_proof(self.merkle_tree, tx_hash)
        return proof if found else []