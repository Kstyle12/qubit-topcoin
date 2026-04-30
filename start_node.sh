#!/bin/bash
cd "$HOME/qubit-topcoin/qtopcore"
source "$HOME/.cargo/env"

PORT=${1:-5003}
ADDRESS=${2:-""}

echo "========================================="
echo "  Starting QTOP Node on port $PORT"
echo "========================================="

if [ -n "$ADDRESS" ]; then
    ./target/release/qtopcore $PORT $ADDRESS
else
    ./target/release/qtopcore $PORT
fi
