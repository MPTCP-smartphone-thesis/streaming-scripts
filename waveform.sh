#!/bin/bash
echo "check dir"
test -d "$1" && echo "dir ok" || exit
waveform --scan "$1/mptcp.mkv" --png-width 1024 --png-height 128 --png-color-center 0f0bbfff --png-color-outer 0f0cc0ff --png "$1/mptcp.png"
waveform --scan "$1/tcp.mkv"   --png-width 1024 --png-height 128 --png-color-center 0f0bbfff --png-color-outer 0f0cc0ff --png "$1/tcp.png"
