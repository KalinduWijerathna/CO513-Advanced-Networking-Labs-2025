#!/bin/bash

SERVER1="172.28.1.11"
SERVER2="172.28.1.12"
PORT="80"
SELECTED_FILE="/tmp/selected_server"

# Initial target
echo "$SERVER1" > "$SELECTED_FILE"

while true; do
    # Simulate random load values between 0 and 100
    LOAD1=$(( RANDOM % 101 ))
    LOAD2=$(( RANDOM % 101 ))

    echo "-------------------------------"
    echo "Simulated random server loads:"
    echo "Server 1 ($SERVER1) load: $LOAD1"
    echo "Server 2 ($SERVER2) load: $LOAD2"

    if [ "$LOAD1" -le "$LOAD2" ]; then
        TARGET="$SERVER1"
    else
        TARGET="$SERVER2"
    fi

    echo "$TARGET" > "$SELECTED_FILE"
    echo "Selected server: $TARGET"

    sleep 5
done
