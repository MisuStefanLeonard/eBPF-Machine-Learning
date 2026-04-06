#!/bin/bash

# 1. Catch the PID passed from Python (Argument $1)
PYTHON_PID=$1
MAP_PATH="/sys/fs/bpf/self_pid_map"

if [ -z "$PYTHON_PID" ]; then
    echo "Error: No PID provided."
    exit 1
fi

# 2. Format the Key (1) into Little Endian Hex: 0x01 0x00 0x00 0x00
KEY_HEX="0x01 0x00 0x00 0x00"

# 3. Format the Python PID into Little Endian Hex (4 bytes)
# Convert PID to an 8-character hex string (e.g., 1234 -> 000004d2)
HEX_STR=$(printf "%08x\n" $PYTHON_PID)

# Split into bytes and reverse the order for Little Endian
B1=$(echo $HEX_STR | cut -c7-8)
B2=$(echo $HEX_STR | cut -c5-6)
B3=$(echo $HEX_STR | cut -c3-4)
B4=$(echo $HEX_STR | cut -c1-2)

VAL_HEX="0x$B1 0x$B2 0x$B3 0x$B4"

# 4. Run the bpftool command
# Notice we put 'sudo' here. We will configure Linux to ignore the password for this specific script.
sudo bpftool map update pinned $MAP_PATH key $KEY_HEX value $VAL_HEX

echo "Successfully injected Python PID ($PYTHON_PID) into $MAP_PATH"