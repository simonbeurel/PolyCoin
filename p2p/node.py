import socket
import threading
import sys
import time

# Fonction pour gérer les connexions entrantes
def handle_client(conn, addr):
    print(f"[NOUVELLE CONNEXION] {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"[{addr}] {data.decode()}")
        conn.sendall(b"Message recu")
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

# Envoyer des messages aux pairs
def send_message(peer, message):
    try:
        peer_ip, peer_port = peer.split(":")
        peer_port = int(peer_port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((peer_ip, peer_port))
        client.sendall(message.encode())
        response = client.recv(1024)
        print(f"[RÉPONSE] {response.decode()}")
        client.close()
    except Exception as e:
        print(f"[ERREUR] Impossible d'envoyer le message: {e}")

def connect_to_peer(peer_ip, peer_port):
    PEERS.append((peer_ip, peer_port))
    print(f"[+] Connecté au pair {peer_ip}:{peer_port}")


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
        else:
            print("[!] Choix invalide.")
