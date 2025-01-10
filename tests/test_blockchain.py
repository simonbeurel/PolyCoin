from blockchain.blockchain import Blockchain
from blockchain.blocks import PolyCoinBlock
from blockchain.merkle_tree import MerkleTree


def test_genesis_block():
    blockchain = Blockchain()
    genesis_block = blockchain.chain[0]
    assert len(blockchain.chain) == 1
    assert genesis_block.type == "CODE"
    assert genesis_block.previous_block_hash == "0"
    assert genesis_block.merkle_root is not None
    assert len(genesis_block.transactions) > 0


def test_add_block():
    blockchain = Blockchain()
    blockchain.create_block_from_source_code("test_code", "test_signature")
    assert len(blockchain.chain) == 2
    new_block = blockchain.last_block
    assert new_block.source_code == "test_code"
    assert new_block.previous_block_hash == blockchain.chain[0].block_hash


def test_block_to_dict():
    block = PolyCoinBlock("0", "test_code", "test_signature")
    block_dict = block.to_dict()
    assert block_dict['type'] == "CODE"
    assert block_dict['source_code'] == "test_code"
    assert 'merkle_root' in block_dict and block_dict['merkle_root'] is not None
    assert 'transactions' in block_dict and len(block_dict['transactions']) > 0


def test_block_merkle_proof():
    block = PolyCoinBlock("0", "test_code", "test_signature")
    tx = "source_code:test_code"
    proof = block.get_merkle_proof(tx)
    tx_hash = MerkleTree.hash_data(tx)
    assert MerkleTree.verify_proof(tx_hash, proof, block.merkle_root)

    # Ajout de cas avec plusieurs transactions
    block.transactions.append("new:transaction")
    block.merkle_tree = MerkleTree.build_tree(block.transactions)
    block.merkle_root = block.merkle_tree.hash
    tx = "new:transaction"
    proof = block.get_merkle_proof(tx)
    tx_hash = MerkleTree.hash_data(tx)
    assert MerkleTree.verify_proof(tx_hash, proof, block.merkle_root)


def test_block_invalid_merkle_proof():
    block = PolyCoinBlock("0", "test_code", "test_signature")
    tx = "invalid:transaction"
    proof = block.get_merkle_proof(tx)
    tx_hash = MerkleTree.hash_data(tx)
    assert not MerkleTree.verify_proof(tx_hash, proof, block.merkle_root)


def test_blockchain_integrity():
    blockchain = Blockchain()
    blockchain.create_block_from_source_code("test_code_1", "signature_1")
    blockchain.create_block_from_source_code("test_code_2", "signature_2")

    for i in range(1, len(blockchain.chain)):
        assert blockchain.chain[i].previous_block_hash == blockchain.chain[i - 1].block_hash


