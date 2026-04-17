import oqs
import hashlib
import json
import time

# --- QTP TRANSACTION SYSTEM ---
# A transaction proves: "I own these coins and I am sending them to you"
# The FALCON-512 signature is the mathematical proof of ownership

def create_transaction(sender_address, recipient_address, amount,
                       private_key_hex, fee=0.001):
    # Fee defaults to 0.001 QTP — users can set higher for faster inclusion
    transaction = {
        "sender":    sender_address,
        "recipient": recipient_address,
        "amount":    amount,
        "fee":       fee,
        "timestamp": time.time()
    }

    transaction_bytes = json.dumps(transaction, sort_keys=True).encode()
    transaction_hash  = hashlib.sha3_256(transaction_bytes).hexdigest()

    private_key_bytes = bytes.fromhex(private_key_hex)
    signer            = oqs.Signature("Falcon-512", secret_key=private_key_bytes)
    signature         = signer.sign(transaction_bytes)

    return {
        "transaction": transaction,
        "hash":        transaction_hash,
        "signature":   signature.hex()
    }


def verify_transaction(signed_transaction, public_key_hex):
    transaction_bytes = json.dumps(
        signed_transaction["transaction"], sort_keys=True
    ).encode()

    public_key_bytes  = bytes.fromhex(public_key_hex)
    verifier          = oqs.Signature("Falcon-512")
    signature_bytes   = bytes.fromhex(signed_transaction["signature"])

    is_valid = verifier.verify(
        transaction_bytes,
        signature_bytes,
        public_key_bytes
    )
    return is_valid


# --- TEST ---
import base58

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

print("Creating two wallets...")
sender    = generate_wallet()
recipient = generate_wallet()

print(f"Sender:    {sender['address']}")
print(f"Recipient: {recipient['address']}")
print("")

print("Creating transaction: 10 QTP + 0.001 QTP fee...")
signed_tx = create_transaction(
    sender_address=    sender["address"],
    recipient_address= recipient["address"],
    amount=            10.0,
    private_key_hex=   sender["private_key"],
    fee=               0.001
)

print(f"Transaction Hash: {signed_tx['hash']}")
print(f"Fee:              {signed_tx['transaction']['fee']} QTP")
print(f"Signature:        {signed_tx['signature'][:40]}...")
print("")

print("Verifying transaction signature...")
is_valid = verify_transaction(signed_tx, sender["public_key"])
print(f"Signature valid: {is_valid}")
print("")

print("Testing tamper detection...")
tampered_tx = dict(signed_tx)
tampered_tx["transaction"] = dict(signed_tx["transaction"])
tampered_tx["transaction"]["amount"] = 1000000.0
is_valid_tampered = verify_transaction(tampered_tx, sender["public_key"])
print(f"Tampered signature valid: {is_valid_tampered}")
print("")
print("If the above is False, your transaction security is working perfectly.")
