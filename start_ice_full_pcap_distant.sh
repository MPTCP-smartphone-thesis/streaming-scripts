#! /bin/bash
DEST_FILE="/home/mptcp/smartphone-ice/.tcpdump_ice_start"
SSH_USER="mptcpdata"
test -n "$1" && DATE="$1" || DATE="test_$(date +%Y%m%d_%H%M%S)"

echo "ssh $SSH_USER \"echo $DATE >> $DEST_FILE\""
ssh $SSH_USER "echo $DATE >> $DEST_FILE"
