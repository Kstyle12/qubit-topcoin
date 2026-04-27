import oqs
import hashlib
import base58

# --- GENERATE A QTOP WALLET ---
# This creates a brand new quantum-resistant keypair using FALCON-512
# Every QTOP wallet starts exactly here

def generate_wallet():
    # Step 1: Create a FALCON-512 signing object
    # This is the quantum-resistant algorithm we chose for QTOP
    signer = oqs.Signature("Falcon-512")

    # Step 2: Generate the public and private keys
    # Public key  = your wallet address (you share this)
    # Private key = your secret key    (you NEVER share this)
    public_key = signer.generate_keypair()
    private_key = signer.export_secret_key()

    # Step 3: Generate the wallet address from the public key
    # We hash the public key with SHA3-256 (our chosen hash algorithm)
    # This converts the large public key into a short, clean address
    sha3_hash = hashlib.sha3_256(public_key).digest()

    # Step 4: Take the last 20 bytes of the hash
    # This is the same approach Bitcoin uses for addresses
    address_bytes = sha3_hash[-20:]

    # Step 5: Add QTOP version byte so address starts with "QT"
    # 0x26 is a version prefix that produces QT addresses in Base58
    versioned = bytes([0x26]) + address_bytes

    # Step 6: Create a checksum — 4 bytes that catch typos in addresses
    checksum = hashlib.sha3_256(
                    hashlib.sha3_256(versioned).digest()
               ).digest()[:4]

    # Step 7: Encode everything into a readable address string
    address = base58.b58encode(versioned + checksum).decode('utf-8')

    return {
        "address":     address,
        "public_key":  public_key.hex(),
        "private_key": private_key.hex()
    }

# --- RUN IT ---
print("Generating your QTOP wallet...")
print("")
wallet = generate_wallet()
print(f"Address:     {wallet['address']}")
print(f"Public Key:  {wallet['public_key'][:40]}...") # truncated for display
print(f"Private Key: {wallet['private_key'][:40]}...") # truncated for display
print("")
print("WARNING: Never share your private key with anyone. Ever.")
