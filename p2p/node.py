import socket
import threading
import sys
import time
import json

from blockchain.blockchain import Blockchain

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
            print("Peers list sended")
        else:
            with open(f"logs/logs_{HOST}:{PORT}.txt", 'a') as f:
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

def broadcast_new_block(block):
    for peer in PEERS:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(peer)
            message = json.dumps({
                'type': 'NEW_BLOCK',
                'block': "This is a new block"
            })
            client.send(message.encode())
            client.close()
        except Exception as e:
            print(f"[!] Impossible to contact {peer}: {e}")


def create_new_block_code():
    print("Which type of block do you want to create ?")
    input_user = input("1. Identifier\n2. Code\n")
    if input_user == '1':
        name_organization = input("Name of the organization : ")
        certificate = input("Certificate : ")
        walletETH = input("Wallet ETH : ")
        public_key_str = input("Public key : ")
        blockchain.create_block_from_identifier(name_organization, public_key_str, certificate, walletETH)
    elif input_user == '2':
        source_code = input("Source code : ")
        signature = input("Signature : ")
        blockchain.create_block_from_source_code(source_code, signature)
    print("\033[92m[+] Block created successfully\033[0m")

if __name__ == "__main__":

    print(r'''
    ___             _      _  _    ___    _                 _            
   | _ \   ___     | |    | || |  / __|  | |_     __ _     (_)    _ _    
   |  _/  / _ \    | |     \_, | | (__   | ' \   / _` |    | |   | ' \   
  _|_|_   \___/   _|_|_   _|__/   \___|  |_||_|  \__,_|   _|_|_  |_||_|  
_| """ |_|"""""|_|"""""|_| """"|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| 
"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-' 
    ''')

    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <IP_HOST> <PORT> [--muted]")
        sys.exit(1)

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    MUTED = '--muted' in sys.argv
    PEERS = []

    blockchain = Blockchain()

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
│ 5. 📡  Test broadcast message HelloWorld  │
│ 6. 🔄  Refresh the peers's list           │
└───────────────────────────────────────────┘
        """)
        choix = input("Choix : ")

        if choix == '1':
            create_new_block_code()
        elif choix == '2':
            peer_ip = input("Peer's IP address : ")
            peer_port = int(input("Peer's port : "))
            connect_to_peer(peer_ip, peer_port)
        elif choix == '3':
            for block in blockchain.chain:
                print("---------------------------")
                print(block.to_dict())
        elif choix == '4':
            print("\n📡 Peers connected :")
            for peer in PEERS:
                print("---------------------------")
                print(f"IP: {peer[0]}:{peer[1]}")
        elif choix == '5':
            broadcast_new_block(None)
        elif choix == '6':
            refresh_list_peers()
        else:
            print("[!] Invalid choice.")
