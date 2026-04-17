import sys
import json
import requests
from flask import Flask, request, jsonify
from blockchain import Blockchain
from block import Block
from transaction import verify_transaction

app = Flask(__name__)
qtpchain = Blockchain()
peers = set()
miner_address = "QTP_NODE_MINER_ADDRESS"

@app.route('/chain', methods=['GET'])
def get_chain():
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
    data = request.get_json()
    required = ["sender", "recipient", "amount", "signature", "public_key"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing transaction fields"}), 400

    is_valid = verify_transaction(
        {
            "transaction": {
                "sender":    data["sender"],
                "recipient": data["recipient"],
                "amount":    data["amount"],
                "fee":       data.get("fee", 0.001),
                "timestamp": data["timestamp"]
            },
            "signature": data["signature"]
        },
        data["public_key"]
    )

    if not is_valid:
        return jsonify({"error": "Invalid signature — transaction rejected"}), 400

    qtpchain.add_transaction({
        "sender":    data["sender"],
        "recipient": data["recipient"],
        "amount":    data["amount"],
        "fee":       data.get("fee", 0.001),
        "timestamp": data["timestamp"]
    })

    broadcast_transaction(data)
    return jsonify({"message": "Transaction added to mempool"}), 201

@app.route('/mine', methods=['GET'])
def mine():
    if len(qtpchain.mempool) == 0:
        return jsonify({"message": "No transactions to mine"}), 200
    block = qtpchain.mine_pending_transactions(miner_address)
    broadcast_block(block)
    return jsonify({
        "message": f"Block {block.index} mined successfully",
        "hash":    block.hash,
        "reward":  qtpchain.get_current_reward()
    })

@app.route('/peers/register', methods=['POST'])
def register_peer():
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
    replaced = sync_with_peers()
    if replaced:
        return jsonify({"message": "Chain replaced with longer peer chain"})
    return jsonify({"message": "Our chain is already the longest"})

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = qtpchain.get_balance(address)
    return jsonify({
        "address": address,
        "balance": balance
    })

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status":      "running",
        "blocks":      len(qtpchain.chain),
        "pending_txs": len(qtpchain.mempool),
        "peers":       list(peers),
        "latest_hash": qtpchain.get_latest_block().hash[:20] + "..."
    })

def broadcast_transaction(transaction_data):
    for peer in peers:
        try:
            requests.post(
                f"{peer}/transactions/new",
                json=transaction_data,
                timeout=3
            )
        except:
            pass

def broadcast_block(block):
    for peer in peers:
        try:
            requests.get(
                f"{peer}/peers/sync",
                timeout=3
            )
        except:
            pass

def sync_with_peers():
    longest_chain = None
    max_length    = len(qtpchain.chain)

    for peer in peers:
        try:
            response    = requests.get(f"{peer}/chain", timeout=3)
            data        = response.json()
            peer_length = data["length"]
            peer_chain  = data["chain"]
            if peer_length > max_length:
                max_length    = peer_length
                longest_chain = peer_chain
        except:
            pass

    if longest_chain:
        print(f"  Replacing chain with longer peer chain "
              f"({max_length} blocks)")
        qtpchain.chain = []
        for block_data in longest_chain:
            block = Block(
                index=         block_data["index"],
                transactions=  block_data["transactions"],
                previous_hash= block_data["previous_hash"]
            )
            block.timestamp = block_data["timestamp"]
            block.nonce     = block_data["nonce"]
            block.hash      = block_data["hash"]
            qtpchain.chain.append(block)
        qtpchain.mempool = []
        return True

    return False

if __name__ == '__main__':
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
