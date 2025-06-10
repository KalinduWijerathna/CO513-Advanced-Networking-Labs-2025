import socket
import time
import random

HOST = 'localhost'
PORT = 9998

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    for i in range(20):
        size = random.randint(500, 2000)  # Random packet size
        data = b'x' * size
        client_socket.sendall(data)

        # Receive server response
        response = client_socket.recv(1024).decode()
        print(f"[Client] Sent {size} bytes | Server: {response}")

        # Random interval between 10ms to 500ms
        time.sleep(random.uniform(0.01, 0.5))

except KeyboardInterrupt:
    print("\n[Client] Interrupted.")
finally:
    client_socket.close()
