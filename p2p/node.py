import socket
import threading
import sys
import time
import json

from blockchain.blockchain import Blockchain
from blockchain.blocks import *


# Fonction pour gérer les connexions entrantes
def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode()
        message = json.loads(data)

        if message['type'] == 'ASK_PEERS_LIST':
            response = {
                'type': 'RECEIVED_PEERS_LIST',
                'data': PEERS
            }
            conn.send(json.dumps(response).encode())
            print("Peers list sent")
        else:
            with open(f"p2p/logs/logs_{HOST}:{PORT}.txt", 'a') as f:
                f.write(f"[{addr[0]}] {message['block']}\n")
                print(message)
    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        conn.close()


# Lancer le serveur
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"\033[93m[+] Node just started at {HOST}:{PORT}\033[0m")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


def connect_to_peer(peer_ip, peer_port):
    PEERS.append((peer_ip, peer_port))
    print(f"\033[92m[+] Connected to the peer {peer_ip}:{peer_port} successfully\033[0m")


def connect_to_validator(validator_ip, validator_port):
    global VALIDATOR, blockchain
    VALIDATOR = (validator_ip, validator_port)
    print(f"\033[92m[+] Connected to validator at {validator_ip}:{validator_port}\033[0m")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(VALIDATOR)
    message = json.dumps({
        'type': 'REQUEST_BLOCKCHAIN'
    })
    client.send(message.encode())
    response = client.recv(4096).decode()
    response_data = json.loads(response)
    if response_data['type'] == 'BLOCKCHAIN':
        print(response_data)
        blockchain = [PolyCoinBlock.from_dict(blocks) for blocks in response_data['chain']]
        print("\033[92m[+] Blockchain synchronized with validator\033[0m")


def get_block_validation(block_data):
    """Envoie un bloc au validateur et attend sa réponse"""
    try:
        if not VALIDATOR:
            print("\033[91m[!] No validator connected. Please connect to a validator first.\033[0m")
            return False, None

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(VALIDATOR)

        message = json.dumps({
            'type': 'NEW_BLOCK',
            'block': block_data
        })
        client.send(message.encode())

        # Attendre la réponse du validateur
        response = client.recv(4096).decode()
        response_data = json.loads(response)

        client.close()

        if response_data['type'] == 'BLOCK_VALIDATED':
            print("\033[92m[+] Block validated successfully\033[0m")
            return True, response_data['block']
        else:
            print(f"\033[91m[!] Block validation failed: {response_data.get('reason', 'Unknown reason')}\033[0m")
            return False, None

    except Exception as e:
        print(f"\033[91m[!] Error during validation: {e}\033[0m")
        return False, None


def refresh_list_peers():
    to_add = []
    for peer in PEERS:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(peer)
            message = json.dumps({
                'type': 'ASK_PEERS_LIST'
            })
            client.send(message.encode())
            response = client.recv(4096).decode()
            response_data = json.loads(response)

            if response_data['type'] == 'RECEIVED_PEERS_LIST':
                for p in response_data['data']:
                    if tuple(p) not in PEERS:
                        to_add.append(tuple(p))
                        print(f"\033[92m[+] New peer added {p[0]}:{p[1]}\033[0m")

            client.close()
        except Exception as e:
            print(f"[!] Impossible to contact {peer}: {e}")

    for peer in to_add:
        PEERS.append(peer)


def broadcast_last_block():
    for peer in PEERS:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(peer)
            message = json.dumps({
                'type': 'NEW_BLOCK',
                'block': blockchain[-1].to_dict()
            })
            client.send(message.encode())
            client.close()
        except Exception as e:
            print(f"[!] Impossible to contact {peer}: {e}")


def create_new_block_code():
    if not VALIDATOR:
        print("\033[91m[!] Please connect to a validator first (option 7)\033[0m")
        return

    print("Which type of block do you want to create ?")
    input_user = input("1. Identifier\n2. Code\n")

    try:
        if input_user == '1':
            name_organization = input("Name of the organization : ")
            certificate = input("Certificate : ")
            walletETH = input("Wallet ETH : ")
            public_key_str = input("Public key : ")
            block_to_be_verified = PolyCoinBlockIdentifier(blockchain[-1].block_hash, name_organization, public_key_str, certificate, walletETH)
        elif input_user == '2':
            source_code = input("Source code : ")
            signature = input("Signature : ")
            block_to_be_verified = PolyCoinBlock(blockchain[-1].block_hash,source_code, signature)
        else:
            print("[!] Invalid choice")
            return

        # Obtenir la validation du block
        is_valid, validated_block = get_block_validation(block_to_be_verified.to_dict())

        if is_valid and validated_block:
            # Mettre à jour le bloc avec les informations du validateur
            block_to_be_verified.validator_signature = validated_block.get('validator_signature')
            block_to_be_verified.validator_address = validated_block.get('validator_address')

            # Ajouter le bloc à la blockchain
            blockchain.append(block_to_be_verified)
            print("\033[92m[+] Block added to blockchain successfully\033[0m")
            broadcast_last_block()
        else:
            print("\033[91m[!] Block was not added to blockchain\033[0m")

    except Exception as e:
        print(f"\033[91m[!] Error creating block: {e}\033[0m")


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
    MUTED = '--muted' in sys.argv
    PEERS = []
    VALIDATOR = None

    blockchain = None

    threading.Thread(target=start_server, daemon=True).start()
    time.sleep(2)

    while True:
        print("""
┌───────────────────────────────────────────┐
│                 MENU                      │
├───────────────────────────────────────────┤
│ 1. 🛠️  Mine a new block                   │
│ 2. 🔗  Connect to a new peer              │
│ 3. 📜  Print the blockchain               │
│ 4. 🌐  Show the connected peers           │
│ 5. 📡  Test broadcast last block mined    │
│ 6. 🔄  Refresh the peers's list           │
│ 7. 🔐  Connect to a validator             │
└───────────────────────────────────────────┘
        """)
        choix = input("Choice : ")

        if choix == '1':
            if blockchain is None:
                print("\033[91m[!] Node is not connected to the blockchain\033[0m")
                continue
            create_new_block_code()
        elif choix == '2':
            peer_ip = input("Peer's IP address : ")
            peer_port = int(input("Peer's port : "))
            connect_to_peer(peer_ip, peer_port)
        elif choix == '3':
            if blockchain is None:
                print("\033[91m[!] Node is not connected to the blockchain\033[0m")
                continue
            for block in blockchain:
                print("---------------------------")
                print(block.to_dict())
        elif choix == '4':
            print("\n📡 Peers connected :")
            for peer in PEERS:
                print("---------------------------")
                print(f"IP: {peer[0]}:{peer[1]}")
        elif choix == '5':
            broadcast_last_block()
        elif choix == '6':
            refresh_list_peers()
        elif choix == '7':
            validator_ip = input("Validator's IP address : ")
            validator_port = int(input("Validator's port : "))
            connect_to_validator(validator_ip, validator_port)
        else:
            print("[!] Invalid choice.")