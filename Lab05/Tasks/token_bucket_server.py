import socket
import threading
import time

HOST = 'localhost'
PORT = 9997

MAX_TOKENS = 10          # Max capacity of the token bucket
TOKEN_REFILL_RATE = 2    # Tokens added per second
TOKENS_PER_PACKET = 1    # Tokens consumed per packet

tokens = MAX_TOKENS
lock = threading.Lock()
processed_count = 0
rejected_count = 0

def refill_tokens():
    global tokens
    while True:
        with lock:
            if tokens < MAX_TOKENS:
                tokens += 1
                print(f"[+] Token added | Tokens now: {tokens}")
        time.sleep(1 / TOKEN_REFILL_RATE)

def main():
    global tokens, processed_count, rejected_count

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[Server] Listening on {HOST}:{PORT}...")

    conn, addr = server_socket.accept()
    print(f"[+] Connection from {addr}")

    # Start the token refiller thread
    threading.Thread(target=refill_tokens, daemon=True).start()

    try:
        while True:
            data = conn.recv(2048)
            if not data:
                break
            with lock:
                if tokens >= TOKENS_PER_PACKET:
                    tokens -= TOKENS_PER_PACKET
                    processed_count += 1
                    print(f"[✔] Packet processed | Tokens left: {tokens}")
                    conn.sendall(b"processed")
                else:
                    rejected_count += 1
                    print(f"[✘] Packet rejected | Insufficient tokens ({tokens})")
                    conn.sendall(b"rejected")
    except:
        print("[!] Connection lost.")

    print(f"\n[Summary] Processed: {processed_count}, Rejected: {rejected_count}")
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    main()
