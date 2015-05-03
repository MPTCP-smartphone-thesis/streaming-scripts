#!/bin/sh
DIR=$1
test ! -d "$1" && echo "$1: not a dir, exit" && exit 1
if test -n "$2"; then
	MAC="$2"
else
	test ! -f "mac.txt" && echo "mac.txt file doesn't exist and no second arg" && exit 1
	MAC=$(head -n 1 mac.txt)
fi

START=$(head -n 1 $DIR/dates.log || exit 1)
END=$(tail -n 1 $DIR/dates.log || exit 1)

ssh -L 27017:localhost:27017 mptcpdata -N &
PID=$!
echo "SSH PID: $PID"
sleep 2

test -d /proc/$PID || exit 1

./gen_map.py -o $DIR --open "$MAC" $START $END

kill $PID
