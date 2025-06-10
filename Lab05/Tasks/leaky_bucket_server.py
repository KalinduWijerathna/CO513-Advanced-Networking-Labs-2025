import socket
import threading
import time
from queue import Queue

HOST = 'localhost'
PORT = 9998
MAX_BUCKET_SIZE = 5        # Max packets the bucket can hold
LEAK_RATE = 1              # Packets per second

bucket = Queue(maxsize=MAX_BUCKET_SIZE)
lock = threading.Lock()
processed_count = 0
dropped_count = 0

def leak_packets(conn):
    global processed_count
    while True:
        with lock:
            if not bucket.empty():
                packet = bucket.get()
                processed_count += 1
                print(f"[✔] Processed packet | Bucket size: {bucket.qsize()}")
                try:
                    conn.sendall(b"processed")
                except:
                    break
        time.sleep(1 / LEAK_RATE)

def main():
    global dropped_count
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[Server] Listening on {HOST}:{PORT}...")

    conn, addr = server_socket.accept()
    print(f"[+] Connection from {addr}")

    # Start leaker thread
    threading.Thread(target=leak_packets, args=(conn,), daemon=True).start()

    try:
        while True:
            data = conn.recv(2048)
            if not data:
                break
            with lock:
                if not bucket.full():
                    bucket.put(data)
                    print(f"[↑] Packet accepted | Bucket size: {bucket.qsize()}")
                else:
                    dropped_count += 1
                    print(f"[✘] Packet dropped  | Bucket FULL ({MAX_BUCKET_SIZE})")
                    conn.sendall(b"dropped")
    except:
        print("[!] Connection lost.")

    print(f"\n[Summary] Processed: {processed_count}, Dropped: {dropped_count}")
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    main()
