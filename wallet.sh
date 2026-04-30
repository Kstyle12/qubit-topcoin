#!/bin/bash
cd "$HOME/qubit-topcoin/qtopcore"
source "$HOME/.cargo/env"
./target/release/qtopwallet "$@"
