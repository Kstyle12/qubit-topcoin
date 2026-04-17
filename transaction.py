import oqs
import hashlib
import json
import time

# --- QTP TRANSACTION SYSTEM ---
# A transaction proves: "I own these coins and I am sending them to you"
# The FALCON-512 signature is the mathematical proof of ownership

def create_transaction(sender_address, recipient_address, amount, private_key_hex):
    # Step 1: Build the transaction data
    # This is the raw message we are going to sign
    # Time is included so two identical payments are never the same transaction
    transaction = {
        "sender":    sender_address,
        "recipient": recipient_address,
        "amount":    amount,
        "timestamp": time.time()
    }

    # Step 2: Convert the transaction to bytes so we can sign it
    # JSON gives us a consistent string, encode() converts it to bytes
    transaction_bytes = json.dumps(transaction, sort_keys=True).encode()

    # Step 3: Hash the transaction data with SHA3-256
    # We sign the hash rather than the raw data — faster and cleaner
    transaction_hash = hashlib.sha3_256(transaction_bytes).hexdigest()

    # Step 4: Sign the hash using FALCON-512 and our private key
    # This is the quantum-resistant proof of ownership
    private_key_bytes = bytes.fromhex(private_key_hex)
    signer = oqs.Signature("Falcon-512", secret_key=private_key_bytes)
    signature = signer.sign(transaction_bytes)

    # Step 5: Return the complete signed transaction
    return {
        "transaction": transaction,
        "hash":        transaction_hash,
        "signature":   signature.hex()
    }


def verify_transaction(signed_transaction, public_key_hex):
    # Step 1: Rebuild the transaction bytes exactly as they were when signed
    transaction_bytes = json.dumps(
        signed_transaction["transaction"], sort_keys=True
    ).encode()

    # Step 2: Recreate the verifier using the sender's public key
    public_key_bytes = bytes.fromhex(public_key_hex)
    verifier = oqs.Signature("Falcon-512")

    # Step 3: Verify the signature
    # Returns True if the signature is valid, False if anything was tampered with
    signature_bytes = bytes.fromhex(signed_transaction["signature"])
    is_valid = verifier.verify(
        transaction_bytes,
        signature_bytes,
        public_key_bytes
    )

    return is_valid


# --- TEST IT ---
# First we need a wallet to test with — reusing our wallet generator
import base58

def generate_wallet():
    signer = oqs.Signature("Falcon-512")
    public_key = signer.generate_keypair()
    private_key = signer.export_secret_key()
    sha3_hash = hashlib.sha3_256(public_key).digest()
    address_bytes = sha3_hash[-20:]
    versioned = bytes([0x26]) + address_bytes
    checksum = hashlib.sha3_256(
                   hashlib.sha3_256(versioned).digest()
               ).digest()[:4]
    address = base58.b58encode(versioned + checksum).decode('utf-8')
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

print("Creating transaction: 10 QTP from sender to recipient...")
signed_tx = create_transaction(
    sender_address=    sender["address"],
    recipient_address= recipient["address"],
    amount=            10.0,
    private_key_hex=   sender["private_key"]
)

print(f"Transaction Hash: {signed_tx['hash']}")
print(f"Signature:        {signed_tx['signature'][:40]}...")
print("")

print("Verifying transaction signature...")
is_valid = verify_transaction(signed_tx, sender["public_key"])
print(f"Signature valid: {is_valid}")
print("")

# Now test that tampering is detected
print("Testing tamper detection...")
tampered_tx = dict(signed_tx)
tampered_tx["transaction"] = dict(signed_tx["transaction"])
tampered_tx["transaction"]["amount"] = 1000000.0
is_valid_tampered = verify_transaction(tampered_tx, sender["public_key"])
print(f"Tampered signature valid: {is_valid_tampered}")
print("")
print("If the above is False, your transaction security is working perfectly.")
