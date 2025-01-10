from .blocks import PolyCoinBlock, PolyCoinBlockIdentifier

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

    def create_block_from_identifier(self, name_organization, public_key_str, certificate, walletETH):
        previous_block_hash = self.last_block.block_hash
        self.chain.append(
            PolyCoinBlockIdentifier(previous_block_hash, name_organization, public_key_str, certificate, walletETH))

    def store_public_key(self, name_organization, public_key_str) -> bool:
        if name_organization not in self.dic_pub_key:
            self.dic_pub_key[name_organization] = public_key_str
            return True
        return False

    @property
    def last_block(self):
        return self.chain[-1]
