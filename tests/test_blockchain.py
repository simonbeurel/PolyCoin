from blockchain.blockchain import Blockchain

def test_genesis_block():
    blockchain = Blockchain()
    assert len(blockchain.chain) == 1
    assert blockchain.chain[0].type == "CODE"

def test_add_block():
    blockchain = Blockchain()
    blockchain.create_block_from_source_code("test_code", "test_signature")
    assert len(blockchain.chain) == 2
    assert blockchain.last_block.source_code == "test_code"
