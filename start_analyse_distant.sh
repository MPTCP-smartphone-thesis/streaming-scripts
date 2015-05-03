#! /bin/bash
[ "$1" = "" ] && echo "No timestamp" && exit 1

DATE="$1"
DEST_FILE="/home/mptcp/smartphone-ice/.analyse_ice_start"
SSH_USER="mptcpdata"

echo "ssh $SSH_USER \"echo $DATE >> $DEST_FILE\""
ssh $SSH_USER "echo $DATE >> $DEST_FILE"
