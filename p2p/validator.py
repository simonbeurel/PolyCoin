import socket
import threading
import sys
import time
import json
from datetime import datetime
import hashlib

from blockchain.blockchain import Blockchain


class Validator:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.blockchain = Blockchain()
        self.private_key = "validator_private_key"

    def sign_block(self, block_data):
        block_hash = hashlib.sha256(
            f"{block_data['timestamp']}{block_data['previous_block_hash']}".encode()
        ).hexdigest()

        signature = hashlib.sha256(
            f"{block_hash}{self.private_key}".encode()
        ).hexdigest()
        return signature

    def validate_block(self, block_data):
        if block_data['type'] == 'IDENTIFIER':
            required_fields = ['type', 'previous_block_hash', 'name_organization', 'public_key_str', 'certificate', 'wallet_eth_address']
        elif block_data['type'] == 'CODE':
            required_fields = ['type', 'previous_block_hash', 'source_code', 'signature']
        else:
            return False, "Invalid block type"
        if not all(field in block_data for field in required_fields):
            return False, "Block missing required fields"

        if block_data['previous_block_hash'] != self.blockchain.last_block.block_hash:
            return False, "Invalid previous hash"

        signature = self.sign_block(block_data)
        block_data['validator_signature'] = signature
        block_data['validator_address'] = f"{self.host}:{self.port}"

        if block_data['type'] == 'IDENTIFIER':
            self.blockchain.create_block_from_identifier(
                block_data['name_organization'],
                block_data['public_key_str'],
                block_data['certificate'],
                block_data['wallet_eth_address']
            )
        elif block_data['type'] == 'CODE':
            self.blockchain.create_block_from_source_code(
                block_data['source_code'],
                block_data['signature']
            )

        return True, block_data


def broadcast_blockchain():
    for peer in LIST_PEERS:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(peer)
            message = json.dumps({
                'type': 'BLOCKCHAIN_CHANGED',
                'chain': [block.to_dict() for block in validator.blockchain.chain]
            })
            client.send(message.encode())
            client.close()
        except Exception as e:
            print(f"\033[91m[!] Impossible to contact peer {peer}:{e}\033[0m")
    print(f"\033[92m[+] Blockchain broadcast successfully\033[0m")

def handle_client(conn, addr, validator):
    try:
        data = conn.recv(4096).decode()
        message = json.loads(data)

        if message['type'] == 'NEW_BLOCK':
            block_data = message['block']
            print(f"\033[93m[*] Received new block from {addr[0]}\033[0m")

            is_valid, result = validator.validate_block(block_data)
            if is_valid:
                response = {
                    'type': 'BLOCK_VALIDATED',
                    'block': result
                }
                print(f"\033[92m[+] Block validated and signed\033[0m")
                broadcast_blockchain()
            else:
                response = {
                    'type': 'BLOCK_REJECTED',
                    'reason': result
                }
                print(f"\033[91m[!] Block rejected: {result}\033[0m")

            conn.send(json.dumps(response).encode())

            # Log the validation result
            with open(f"p2p/logs/logs_{validator.host}:{validator.port}.txt", 'a') as f:
                f.write(f"[{datetime.now()}] Block from {addr[0]}: {'VALIDATED' if is_valid else 'REJECTED'}\n")

        elif message['type'] == 'REQUEST_BLOCKCHAIN':
            response = {
                'type': 'BLOCKCHAIN',
                'chain': [block.to_dict() for block in validator.blockchain.chain]
            }
            conn.send(json.dumps(response).encode())

            ip_sender = message['ip_sender']
            port_sender = message['port_sender']
            LIST_PEERS.append((ip_sender, port_sender))

            print(f"\033[93m[*] Sent blockchain to {addr[0]}\033[0m")

    except Exception as e:
        print(f"\033[91m[!] Error with {addr}: {e}\033[0m")
    finally:
        conn.close()


def start_server(validator):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((validator.host, validator.port))
    server.listen()
    print(f"\033[93m[+] Validator started at {validator.host}:{validator.port}\033[0m")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr, validator)
        ).start()


if __name__ == "__main__":
    print(r'''
    ___             _      _  _    ___    _                 _            
   | _ \   ___     | |    | || |  / __|  | |_     __ _     (_)    _ _    
   |  _/  / _ \    | |     \_, | | (__   | ' \   / _` |    | |   | ' \   
  _|_|_   \___/   _|_|_   _|__/   \___|  |_||_|  \__,_|   _|_|_  |_||_|  
_| """ |_|"""""|_|"""""|_| """"|_|"""""|_|"""""|_|"""""|_|"""""| 
"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-' 
    ''')

    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <IP_HOST> <PORT> [--muted]")
        sys.exit(1)

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    LIST_PEERS = []

    # Initialiser le validateur
    validator = Validator(HOST, PORT)

    # Démarrer le serveur
    start_server(validator)