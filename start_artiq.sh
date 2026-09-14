#!/bin/bash

HOST_IP="10.137.1.249"

MASTER_SESSION="artiq_master"
CTLMGR_SESSION="artiq_ctlmgr"

# Kill existing sessions if they exist
tmux kill-session -t "$MASTER_SESSION" 2>/dev/null
tmux kill-session -t "$CTLMGR_SESSION" 2>/dev/null

# Start fresh sessions
tmux new-session -d -s "$MASTER_SESSION" \
    "artiq_master --no-localhost-bind --bind $HOST_IP"

tmux new-session -d -s "$CTLMGR_SESSION" \
    "artiq_ctlmgr -s $HOST_IP --bind '*'"

echo "Restarted ARTIQ services."
echo
tmux ls
