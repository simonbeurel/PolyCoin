import datetime
from blockchain.blocks import PolyCoinBlock, PolyCoinBlockIdentifier

def test_block_creation():
    block = PolyCoinBlock("0", "test_code", "test_signature")
    assert block.previous_block_hash == "0"
    assert block.source_code == "test_code"
    assert block.type == "CODE"
    assert isinstance(block.timestamp, datetime.datetime)

def test_identifier_block():
    block = PolyCoinBlockIdentifier(
        "0", "test_organization", b"public_key", "certificate", "wallet_address"
    )
    assert block.name_organization == "test_organization"
    assert block.walletETH == "wallet_address"
    assert block.type == "IDENTIFIER"
