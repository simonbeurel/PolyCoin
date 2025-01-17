import socket
import threading
import sys
import time
import json

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
            print(message)
    except Exception as e:
        print(f"[!] Erreur avec {addr}: {e}")
    finally:
        conn.close()

# Lancer le serveur
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[+] Nœud démarré sur {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr)).start()

def connect_to_peer(peer_ip, peer_port):
    PEERS.append((peer_ip, peer_port))
    print(f"[+] Connecté au pair {peer_ip}:{peer_port}")


def refresh_list_peers():
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
                        PEERS.append(tuple(p))
                        print(f"[+] Nouveau pair ajouté : {p[0]}:{p[1]}")
                        
            client.close()
        except Exception as e:
            print(f"[!] Impossible de contacter {peer}: {e}")



def broadcast_new_block(block):
    for peer in PEERS:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(peer)
            message = json.dumps({
                'type': 'NEW_BLOCK',
                'block': "Ceci est un nouveau block"
            })
            client.send(message.encode())
            client.close()
        except Exception as e:
            print(f"[!] Impossible de contacter {peer}: {e}")


if __name__ == "__main__":

    # Vérification des arguments
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <IP_HOST> <PORT> [--muted]")
        sys.exit(1)

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    MUTED = '--muted' in sys.argv
    PEERS = []

    threading.Thread(target=start_server, daemon=True).start()
    time.sleep(2)
    

    while True:
        print("\n1. Miner un bloc [-- NOT DONE YET --]")
        print("2. Connecter à un pair")
        print("3. Afficher la blockchain [-- NOT DONE YET --]")
        print("4. Afficher la liste des pairs connectés")
        print("5. Test broadcast message HelloWorld")
        print("6. Rafraichir la liste de PEERS")
        choix = input("Choix : ")

        if choix == '1':
            print("[-- NOT DONE YET --]")
        elif choix == '2':
            peer_ip = input("IP du pair : ")
            peer_port = int(input("Port du pair : "))
            connect_to_peer(peer_ip, peer_port)
        elif choix == '3':
            print("[-- NOT DONE YET --]")
        elif choix == '4':
            for peer in PEERS:
                print("---------------------------")
                print(f"IP: {peer[0]}:{peer[1]}")
        elif choix == '5':
            broadcast_new_block(None)
        elif choix == '6':
            refresh_list_peers()
        else:
            print("[!] Choix invalide.")
