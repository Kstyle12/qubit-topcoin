import oqs
import hashlib
import base58
import json
import time
import requests

def generate_wallet():
    signer      = oqs.Signature("Falcon-512")
    public_key  = signer.generate_keypair()
    private_key = signer.export_secret_key()
    sha3_hash   = hashlib.sha3_256(public_key).digest()
    address_bytes = sha3_hash[-20:]
    versioned   = bytes([0x26]) + address_bytes
    checksum    = hashlib.sha3_256(
                      hashlib.sha3_256(versioned).digest()
                  ).digest()[:4]
    address     = base58.b58encode(versioned + checksum).decode('utf-8')
    return {
        "address":     address,
        "public_key":  public_key.hex(),
        "private_key": private_key.hex()
    }

def send_transaction(sender, recipient_address, amount, node_url, fee=0.001):
    transaction = {
        "sender":    sender["address"],
        "recipient": recipient_address,
        "amount":    amount,
        "fee":       fee,
        "timestamp": time.time()
    }

    transaction_bytes = json.dumps(transaction, sort_keys=True).encode()
    private_key_bytes = bytes.fromhex(sender["private_key"])
    signer            = oqs.Signature("Falcon-512", secret_key=private_key_bytes)
    signature         = signer.sign(transaction_bytes)

    payload = {
        "sender":     transaction["sender"],
        "recipient":  transaction["recipient"],
        "amount":     transaction["amount"],
        "fee":        transaction["fee"],
        "timestamp":  transaction["timestamp"],
        "signature":  signature.hex(),
        "public_key": sender["public_key"]
    }

    response = requests.post(
        f"{node_url}/transactions/new",
        json=payload
    )
    return response.json()

# --- TEST ---
if __name__ == "__main__":
    print("Generating sender wallet...")
    sender = generate_wallet()
    print(f"Sender address: {sender['address']}")
    print("")

    print("Generating recipient wallet...")
    recipient = generate_wallet()
    print(f"Recipient address: {recipient['address']}")
    print("")

    print("Signing and submitting transaction to node 5001...")
    result = send_transaction(
        sender=            sender,
        recipient_address= recipient["address"],
        amount=            10.0,
        node_url=          "http://localhost:5001",
        fee=               0.001
    )
    print(f"Node response: {result}")
    print("")
    print("Now run: curl http://localhost:5001/mine")
