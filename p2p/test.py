import socket
import threading
import sys

# Vérification des arguments
if len(sys.argv) < 3:
    print(f"Usage: python {sys.argv[0]} <IP_HOST> <PORT> [--muted]")
    sys.exit(1)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
MUTED = '--muted' in sys.argv

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
    print(f"[EN ATTENTE] Connexions sur {HOST}:{PORT}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[CONNEXIONS ACTIVES] {threading.active_count() - 1}")

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

# Exécution du serveur dans un thread
threading.Thread(target=start_server, daemon=True).start()

# Interface d'envoi de messages si non muté
if not MUTED:
    while True:
        peer = input("Entrez IP:PORT du pair : ")
        msg = input("Message : ")
        send_message(peer, msg)
else:
    print("[MODE SILENCIEUX] Le mode réception uniquement est activé.")
    while True:
        continue
