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

def send_transaction(sender, recipient_address, amount_qtp, node_url, fee_qtp=0.001):
    # Convert to cori integers
    amount_cori = int(amount_qtp * 100_000_000)
    fee_cori    = int(fee_qtp * 100_000_000)
    timestamp   = int(time.time())

    # Build transaction — must match Python JSON format
    transaction = {
        "amount":    amount_cori,
        "fee":       fee_cori,
        "recipient": recipient_address,
        "sender":    sender["address"],
        "timestamp": timestamp
    }

    # Sign the sorted JSON bytes — same as Rust expects for Python format
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

    print(f"  Status code: {response.status_code}")
    print(f"  Response: {response.text}")
    return response.text

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

    print("Signing and submitting transaction to Rust node 5003...")
    result = send_transaction(
        sender=            sender,
        recipient_address= recipient["address"],
        amount_qtp=        10.0,
        node_url=          "http://localhost:5003",
        fee_qtp=           0.001
    )
