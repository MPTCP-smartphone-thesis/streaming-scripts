#!/bin/bash

DATE_START=$(date +%s000)
echo "Start: $DATE_START"
./start_ice_full_pcap_distant.sh $DATE_START || exit 1

DIR="traces/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DIR"
echo $DATE_START > "$DIR/dates.log"

echo "Don't forget to:"
echo -e "\t* Enable GPS"
echo -e "\t* Disable 'Save power GPS' and 'Save battery'"
echo -e "\t* Record sound (Shou needs to be relaunched)"
echo -e "\t* Check that Network-Monitor' speed tests have been disabled"
echo -e "\t* Launch streaming radio"
echo
echo "Press Enter to stop capturing"

read
DATE_END=$(date +%s000)
echo "Stop: $DATE_END"
echo $DATE_END >> "$DIR/dates.log"
./stop_ice_full_pcap_distant.sh

BASE="mptcpdata:/home/mptcp/smartphone-ice"
scp "$BASE/mptcp/mptcp_ice_${DATE_START}.pcap" "$BASE/tcp/tcp_ice_${DATE_START}.pcap" "$DIR/"
