#! /bin/bash
# Usage: ./start_analyse_listener.sh [ANALYSE_DIR]

[ "$1" != "" ] && ANALYSE_DIR=$1 || ANALYSE_DIR="/home/mptcp/smartphone-ice/pcap-measurement"

BASE="/home/mptcp/smartphone-ice"
FILE="${BASE}/.analyse_ice_start"
PID="$FILE.pid"

# increase limit to avoid crashes of mptcptrace (it will open a lot of files)
ulimit -n 4096 # default max value
ulimit -n 51200 # try a bigger one

analyse() {
    echo "Analyse $i, log: $2"
    ./analyze.py -i "$1" -p '_ice' -C -W >> "$2" 2>&1 &
    PID_CURR=$!
    echo $PID_CURR >> "$PID"
    wait $PID_CURR && date -R > "$1.done"
}

cd "$ANALYSE_DIR"

> $FILE
chmod 777 "$FILE"
while inotifywait -e modify "$FILE"; do
    git pull

    # The last line of .analyse_ice_start contains the timestamp to analyse
    TIMESTAMP=$(tail -n 1 "$FILE" || echo "UNKNOWN")

    MPTCP="${BASE}/mptcp/mptcp_ice_${TIMESTAMP}.pcap"
    TCP="${BASE}/tcp/tcp_ice_${TIMESTAMP}.pcap"

    mkdir -p pcap
    LOG_NAME="pcap/log_${TIMESTAMP}_$(date +%Y%m%d_%H%M%S)"
    LOG_MPTCP="${LOG_NAME}_mptcp.txt"
    LOG_TCP="${LOG_NAME}_tcp.txt"

    GIT=$(git describe --abbrev=0 --dirty --always)
    echo $GIT > "$LOG_MPTCP"
    echo $GIT > "$LOG_TCP"

    # For any
    (analyse "$MPTCP" "$LOG_MPTCP" &)
    (analyse "$TCP" "$LOG_TCP" &)
done
