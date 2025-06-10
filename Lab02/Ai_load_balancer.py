import time

SERVER1 = "172.28.1.11"
SERVER2 = "172.28.1.12"
SELECTED_FILE = "/tmp/selected_server"

# Track how many times each server was selected
request_history = {
    SERVER1: 0,
    SERVER2: 0
}

def select_server():
    # Pick the server with fewer requests
    if request_history[SERVER1] <= request_history[SERVER2]:
        return SERVER1
    else:
        return SERVER2

def write_selected_server(server):
    with open(SELECTED_FILE, "w") as f:
        f.write(server)

def main():
    print("AI Load Balancer started using request history tracking...\n")

    while True:
        selected = select_server()
        request_history[selected] += 1
        write_selected_server(selected)

        print("-------------------------------")
        print(f"Selected server: {selected}")
        print("-------------------------------")

        time.sleep(1)

if __name__ == "__main__":
    main()

