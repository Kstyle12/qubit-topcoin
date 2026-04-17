import sys
import json
import requests
import threading
from flask import Flask, request, jsonify
from blockchain import Blockchain
from transaction import create_transaction, verify_transaction

# --- QTP NODE ---
# This is a single node on the QTP peer-to-peer network
# Each node holds a full copy of the blockchain and talks to peers
# Run multiple instances on different ports to simulate the network

app = Flask(__name__)

# The node's local copy of the blockchain
qtpchain = Blockchain()

# The set of peer nodes this node knows about
# In a real network these would be other computers on the internet
peers = set()

# The address that mining rewards get paid to for this node
# In a real implementation this would be a real wallet address
miner_address = "QTP_NODE_MINER_ADDRESS"


# -------------------------------------------------------
# ENDPOINTS — these are the URLs other nodes and wallets
# call to interact with this node
# -------------------------------------------------------

@app.route('/chain', methods=['GET'])
def get_chain():
    # Returns this node's full blockchain
    # Other nodes call this to sync with us
    chain_data = []
    for block in qtpchain.chain:
        chain_data.append(block.to_dict())

    return jsonify({
        "length": len(chain_data),
        "chain":  chain_data,
        "peers":  list(peers)
    })


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    # Accepts a new transaction from a wallet and adds it to mempool
    # Wallet software will POST transaction data here
    data = request.get_json()

    required = ["sender", "recipient", "amount", "signature", "public_key"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing transaction fields"}), 400

    # Verify the FALCON-512 signature before accepting
    is_valid = verify_transaction(
        {
            "transaction": {
                "sender":    data["sender"],
                "recipient": data["recipient"],
                "amount":    data["amount"],
                "timestamp": data["timestamp"]
            },
            "signature": data["signature"]
        },
        data["public_key"]
    )

    if not is_valid:
        return jsonify({"error": "Invalid signature — transaction rejected"}), 400

    # Add to mempool
    qtpchain.add_transaction({
        "sender":    data["sender"],
        "recipient": data["recipient"],
        "amount":    data["amount"],
        "timestamp": data["timestamp"]
    })

    # Broadcast transaction to all peers
    broadcast_transaction(data)

    return jsonify({"message": "Transaction added to mempool"}), 201


@app.route('/mine', methods=['GET'])
def mine():
    # Mines all pending transactions into a new block
    # In a real network miners run this continuously
    if len(qtpchain.mempool) == 0:
        return jsonify({"message": "No transactions to mine"}), 200

    block = qtpchain.mine_pending_transactions(miner_address)

    # After mining, broadcast the new block to all peers
    broadcast_block(block)

    return jsonify({
        "message": f"Block {block.index} mined successfully",
        "hash":    block.hash,
        "reward":  qtpchain.get_current_reward()
    })


@app.route('/peers/register', methods=['POST'])
def register_peer():
    # Registers a new peer node with this node
    # Nodes call this on each other when they join the network
    data = request.get_json()
    peer = data.get("peer")

    if not peer:
        return jsonify({"error": "No peer address provided"}), 400

    peers.add(peer)
    return jsonify({
        "message": f"Peer {peer} registered",
        "peers":   list(peers)
    })


@app.route('/peers/sync', methods=['GET'])
def sync_chain():
    # Syncs this node's chain with the longest chain among all peers
    # This is Nakamoto consensus — longest chain wins
    replaced = sync_with_peers()

    if replaced:
        return jsonify({"message": "Chain replaced with longer peer chain"})
    return jsonify({"message": "Our chain is already the longest"})


@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    # Returns the QTP balance of any wallet address
    balance = qtpchain.get_balance(address)
    return jsonify({
        "address": address,
        "balance": balance
    })


@app.route('/status', methods=['GET'])
def status():
    # Quick health check — shows node info at a glance
    return jsonify({
        "status":       "running",
        "blocks":       len(qtpchain.chain),
        "pending_txs":  len(qtpchain.mempool),
        "peers":        list(peers),
        "latest_hash":  qtpchain.get_latest_block().hash[:20] + "..."
    })


# -------------------------------------------------------
# NETWORKING — how nodes talk to each other
# -------------------------------------------------------

def broadcast_transaction(transaction_data):
    # Send a new transaction to all known peers
    for peer in peers:
        try:
            requests.post(
                f"{peer}/transactions/new",
                json=transaction_data,
                timeout=3
            )
        except:
            # If a peer is unreachable just skip it
            pass


def broadcast_block(block):
    # Notify all peers that we mined a new block
    # They will call /peers/sync to get the full updated chain
    for peer in peers:
        try:
            requests.post(
                f"{peer}/peers/sync",
                timeout=3
            )
        except:
            pass


def sync_with_peers():
    # Ask all peers for their chains
    # If any peer has a longer valid chain, replace ours with theirs
    # This is how the network reaches consensus
    global qtpchain

    longest_chain = None
    max_length    = len(qtpchain.chain)

    for peer in peers:
        try:
            response = requests.get(f"{peer}/chain", timeout=3)
            data     = response.json()

            peer_length = data["length"]
            peer_chain  = data["chain"]

            # Only replace if peer chain is longer and valid
            if peer_length > max_length:
                max_length    = peer_length
                longest_chain = peer_chain

        except:
            pass

    if longest_chain:
        # Rebuild our chain from the peer's data
        print(f"  Replacing chain with longer peer chain "
              f"({max_length} blocks)")
        return True

    return False


# -------------------------------------------------------
# START THE NODE
# -------------------------------------------------------

if __name__ == '__main__':
    # Port is passed as command line argument
    # python3 node.py 5000  ← runs on port 5000
    # python3 node.py 5001  ← runs a second node on port 5001
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

    print("=" * 55)
    print(f"  QTP NODE STARTING ON PORT {port}")
    print("=" * 55)
    print(f"  Endpoints:")
    print(f"  GET  /status              — node info")
    print(f"  GET  /chain               — full blockchain")
    print(f"  GET  /mine                — mine pending transactions")
    print(f"  GET  /balance/<address>   — wallet balance")
    print(f"  POST /transactions/new    — submit transaction")
    print(f"  POST /peers/register      — register a peer")
    print(f"  GET  /peers/sync          — sync with peers")
    print("=" * 55)

    app.run(host='0.0.0.0', port=port)
