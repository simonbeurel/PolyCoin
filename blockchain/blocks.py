import hashlib
import datetime


class PolyCoinBlock:
    def __init__(self, previous_block_hash, source_code, signature):
        self.type = "CODE"
        self.previous_block_hash = previous_block_hash
        self.source_code = source_code
        self.timestamp = datetime.datetime.now()
        self.signature = signature
        self.block_data = f"{source_code} - {previous_block_hash} - {self.timestamp}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()

    def to_dict(self):
        return {
            'type': self.type,
            'previous_block_hash': self.previous_block_hash,
            'source_code': self.source_code,
            'timestamp': str(self.timestamp),
            'block_hash': self.block_hash,
            'signature': self.signature
        }


class PolyCoinBlockIdentifier:
    def __init__(self, previous_block_hash, name_organization, public_key_str, certificate, wallet_eth_address):
        self.type = "IDENTIFIER"
        self.name_organization = name_organization
        self.public_key_str = public_key_str
        self.certificate = certificate
        self.walletETH = wallet_eth_address
        self.timestamp = datetime.datetime.now()
        self.block_data = f"{name_organization} - {previous_block_hash} - {self.timestamp}"
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
            'wallet_eth_address': self.walletETH
        }
