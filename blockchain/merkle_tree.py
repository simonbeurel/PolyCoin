import hashlib
from typing import List, Optional


class MerkleNode:
    def __init__(self, hash_value: str, data: str = None, left: Optional['MerkleNode'] = None,
                 right: Optional['MerkleNode'] = None):
        self.hash = hash_value
        self.data = data  # Store original data for leaf nodes
        self.left = left
        self.right = right


class MerkleTree:
    @staticmethod
    def hash_data(data: str) -> str:
        """Hash the input data using SHA256."""
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def create_leaf_nodes(transactions: List[str]) -> List[MerkleNode]:
        """Create leaf nodes from transaction data."""
        return [MerkleNode(MerkleTree.hash_data(tx), tx) for tx in transactions]

    @staticmethod
    def build_tree(transactions: List[str]) -> Optional[MerkleNode]:
        """Build a Merkle tree from a list of transactions."""
        if not transactions:
            return None

        # Create leaf nodes
        nodes = MerkleTree.create_leaf_nodes(transactions)

        # Keep building levels until we reach the root
        while len(nodes) > 1:
            level = []

            # Process nodes in pairs
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                # If we have an odd number of nodes, duplicate the last one
                right = nodes[i + 1] if i + 1 < len(nodes) else left

                # Combine the hashes of the children
                combined_hash = MerkleTree.hash_data(left.hash + right.hash)
                parent = MerkleNode(combined_hash, left=left, right=right)
                level.append(parent)

            nodes = level

        return nodes[0]  # Return the root node

    @staticmethod
    def get_proof(node: MerkleNode, target_hash: str, proof: List[tuple[str, bool]] = None, found: bool = False) -> \
    tuple[List[tuple[str, bool]], bool]:
        """
        Generate a Merkle proof for a given transaction hash using recursive traversal.

        Args:
            node: Current node in traversal
            target_hash: Hash we're looking for
            proof: Current proof path
            found: Whether we've found the target hash

        Returns:
            Tuple of (proof_path, found_flag)
        """
        if proof is None:
            proof = []

        # Base case: leaf node
        if not node.left and not node.right:
            return proof, node.hash == target_hash

        # Recurse left
        if node.left:
            left_proof, found = MerkleTree.get_proof(node.left, target_hash, proof, found)
            if found:
                if node.right:  # Add right sibling to proof
                    proof.append((node.right.hash, False))
                return proof, True

        # Recurse right
        if node.right:
            right_proof, found = MerkleTree.get_proof(node.right, target_hash, proof, found)
            if found:
                proof.append((node.left.hash, True))
                return proof, True

        return proof, found

    @staticmethod
    def verify_proof(tx_hash: str, proof: List[tuple[str, bool]], root_hash: str) -> bool:
        """
        Verify that a transaction is included in the tree using a Merkle proof.
        """
        current_hash = tx_hash

        for sibling_hash, is_left_sibling in proof:
            if is_left_sibling:
                current_hash = MerkleTree.hash_data(sibling_hash + current_hash)
            else:
                current_hash = MerkleTree.hash_data(current_hash + sibling_hash)

        return current_hash == root_hash

