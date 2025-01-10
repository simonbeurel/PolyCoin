import unittest

from blockchain.blockchain import Blockchain
from blockchain.blocks import PolyCoinBlock
from blockchain.merkle_tree import MerkleTree


class ClassicTest(unittest.TestCase):
    def test_genesis_block(self):
        blockchain = Blockchain()
        genesis_block = blockchain.chain[0]
        assert len(blockchain.chain) == 1
        assert genesis_block.type == "CODE"
        assert genesis_block.previous_block_hash == "0"
        assert genesis_block.merkle_root is not None
        assert len(genesis_block.transactions) > 0

    def test_add_block(self):
        blockchain = Blockchain()
        blockchain.create_block_from_source_code("test_code", "test_signature")
        assert len(blockchain.chain) == 2
        new_block = blockchain.last_block
        assert new_block.source_code == "test_code"
        assert new_block.previous_block_hash == blockchain.chain[0].block_hash

    def test_block_to_dict(self):
        block = PolyCoinBlock("0", "test_code", "test_signature")
        block_dict = block.to_dict()
        assert block_dict['type'] == "CODE"
        assert block_dict['source_code'] == "test_code"
        assert 'merkle_root' in block_dict and block_dict['merkle_root'] is not None
        assert 'transactions' in block_dict and len(block_dict['transactions']) > 0

    def test_block_merkle_proof(self):
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

    def test_block_invalid_merkle_proof(self):
        block = PolyCoinBlock("0", "test_code", "test_signature")
        tx = "invalid:transaction"
        proof = block.get_merkle_proof(tx)
        tx_hash = MerkleTree.hash_data(tx)
        assert not MerkleTree.verify_proof(tx_hash, proof, block.merkle_root)

    def test_blockchain_integrity(self):
        blockchain = Blockchain()
        blockchain.create_block_from_source_code("test_code_1", "signature_1")
        blockchain.create_block_from_source_code("test_code_2", "signature_2")

        for i in range(1, len(blockchain.chain)):
            assert blockchain.chain[i].previous_block_hash == blockchain.chain[i - 1].block_hash

class TestMerkleTree(unittest.TestCase):
    def test_empty_transactions(self):
        """Test MerkleTree avec une liste vide de transactions."""
        merkle_tree = MerkleTree.build_tree([])
        self.assertIsNone(merkle_tree)

    def test_single_transaction(self):
        """Test MerkleTree avec une seule transaction."""
        transactions = ["transaction_1"]
        merkle_tree = MerkleTree.build_tree(transactions)
        self.assertIsNotNone(merkle_tree)
        self.assertEqual(merkle_tree.hash, MerkleTree.hash_data(transactions[0]))

    def test_multiple_transactions(self):
        """Test MerkleTree avec plusieurs transactions."""
        transactions = ["tx1", "tx2", "tx3", "tx4"]
        merkle_tree = MerkleTree.build_tree(transactions)
        self.assertIsNotNone(merkle_tree)

        # Vérification de la racine
        combined_hash = MerkleTree.hash_data(
            MerkleTree.hash_data("tx1") + MerkleTree.hash_data("tx2")
        )
        combined_hash_2 = MerkleTree.hash_data(
            MerkleTree.hash_data("tx3") + MerkleTree.hash_data("tx4")
        )
        expected_root_hash = MerkleTree.hash_data(combined_hash + combined_hash_2)
        self.assertEqual(merkle_tree.hash, expected_root_hash)

    def test_valid_merkle_proof(self):
        """Test la preuve Merkle pour une transaction valide."""
        transactions = ["tx1", "tx2", "tx3"]
        merkle_tree = MerkleTree.build_tree(transactions)

        # Générer la preuve pour une transaction
        target_tx = "tx2"
        proof, found = MerkleTree.get_proof(merkle_tree, MerkleTree.hash_data(target_tx))
        self.assertTrue(found)

        # Vérifier la preuve
        root_hash = merkle_tree.hash
        tx_hash = MerkleTree.hash_data(target_tx)
        self.assertTrue(MerkleTree.verify_proof(tx_hash, proof, root_hash))

    def test_invalid_merkle_proof(self):
        """Test la preuve Merkle pour une transaction invalide."""
        transactions = ["tx1", "tx2", "tx3"]
        merkle_tree = MerkleTree.build_tree(transactions)

        # Preuve pour une transaction inexistante
        target_tx = "invalid_tx"
        proof, found = MerkleTree.get_proof(merkle_tree, MerkleTree.hash_data(target_tx))
        self.assertFalse(found)

        # Vérification de la preuve (doit échouer)
        root_hash = merkle_tree.hash
        tx_hash = MerkleTree.hash_data(target_tx)
        self.assertFalse(MerkleTree.verify_proof(tx_hash, proof, root_hash))

    def test_odd_number_of_transactions(self):
        """Test MerkleTree avec un nombre impair de transactions."""
        transactions = ["tx1", "tx2", "tx3"]
        merkle_tree = MerkleTree.build_tree(transactions)
        self.assertIsNotNone(merkle_tree)

        # Vérification de la racine
        combined_hash = MerkleTree.hash_data(
            MerkleTree.hash_data("tx1") + MerkleTree.hash_data("tx2")
        )
        combined_hash_2 = MerkleTree.hash_data(
            MerkleTree.hash_data("tx3") + MerkleTree.hash_data("tx3")
        )
        expected_root_hash = MerkleTree.hash_data(combined_hash + combined_hash_2)
        self.assertEqual(merkle_tree.hash, expected_root_hash)

