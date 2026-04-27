import oqs
import hashlib
import base58
import json
import os
import getpass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# --- QTOP WALLET MANAGER ---
# Generates, encrypts, saves, and loads QTOP wallets
# Your private key is never stored in plain text

def generate_wallet():
    # Generate a fresh FALCON-512 keypair
    signer     = oqs.Signature("Falcon-512")
    public_key = signer.generate_keypair()
    private_key = signer.export_secret_key()

    # Derive wallet address from public key
    sha3_hash    = hashlib.sha3_256(public_key).digest()
    address_bytes = sha3_hash[-20:]
    versioned    = bytes([0x26]) + address_bytes
    checksum     = hashlib.sha3_256(
                       hashlib.sha3_256(versioned).digest()
                   ).digest()[:4]
    address      = base58.b58encode(versioned + checksum).decode('utf-8')

    return {
        "address":     address,
        "public_key":  public_key.hex(),
        "private_key": private_key.hex()
    }


def derive_key(password: str, salt: bytes) -> bytes:
    # Derives a 256-bit AES encryption key from a password
    # PBKDF2 makes brute forcing the password extremely slow
    # 480,000 iterations means millions of guesses per second
    # becomes thousands — protecting weak passwords too
    kdf = PBKDF2HMAC(
        algorithm=  hashes.SHA256(),
        length=     32,
        salt=       salt,
        iterations= 480000,
    )
    return kdf.derive(password.encode())


def save_wallet(wallet: dict, filename: str, password: str):
    # Encrypt and save wallet to a .qtp file
    # The private key is encrypted with AES-256-GCM
    # AES-GCM also detects tampering — wrong password = decryption fails

    # Generate a random salt for key derivation
    # Different salt every time means same password = different key
    salt = os.urandom(16)

    # Derive encryption key from password
    key  = derive_key(password, salt)

    # Generate random nonce for AES-GCM
    nonce = os.urandom(12)

    # Encrypt the private key
    aesgcm          = AESGCM(key)
    private_key_bytes = bytes.fromhex(wallet["private_key"])
    encrypted_key   = aesgcm.encrypt(nonce, private_key_bytes, None)

    # Build the wallet file — only private key is encrypted
    # Address and public key are safe to store in plain text
    wallet_data = {
        "version":       "1.0",
        "address":       wallet["address"],
        "public_key":    wallet["public_key"],
        "encrypted_key": encrypted_key.hex(),
        "salt":          salt.hex(),
        "nonce":         nonce.hex()
    }

    # Save to file
    with open(filename, 'w') as f:
        json.dump(wallet_data, f, indent=2)

    print(f"  Wallet saved to {filename}")


def load_wallet(filename: str, password: str):
    # Load and decrypt a wallet from a .qtp file
    # Wrong password raises an error — private key stays protected

    with open(filename, 'r') as f:
        wallet_data = json.load(f)

    # Reconstruct the encryption key from password and stored salt
    salt = bytes.fromhex(wallet_data["salt"])
    key  = derive_key(password, salt)

    # Decrypt the private key
    nonce         = bytes.fromhex(wallet_data["nonce"])
    encrypted_key = bytes.fromhex(wallet_data["encrypted_key"])
    aesgcm        = AESGCM(key)

    try:
        private_key_bytes = aesgcm.decrypt(nonce, encrypted_key, None)
    except Exception:
        # Wrong password causes decryption to fail here
        raise ValueError("Wrong password — cannot decrypt wallet")

    return {
        "address":     wallet_data["address"],
        "public_key":  wallet_data["public_key"],
        "private_key": private_key_bytes.hex()
    }


def create_new_wallet(filename: str):
    # Full flow — generate wallet, get password, save encrypted file
    print("\n=== CREATE NEW QTOP WALLET ===\n")

    print("Generating FALCON-512 keypair...")
    wallet = generate_wallet()
    print(f"Address: {wallet['address']}")
    print("")

    # Get password securely — characters hidden as you type
    while True:
        password = getpass.getpass("Enter wallet password: ")
        confirm  = getpass.getpass("Confirm password: ")
        if password == confirm:
            break
        print("Passwords do not match. Try again.")

    print("\nEncrypting wallet...")
    save_wallet(wallet, filename, password)

    print("\n=== WALLET CREATED ===")
    print(f"Address:  {wallet['address']}")
    print(f"File:     {filename}")
    print("\nWARNING: If you forget your password your wallet")
    print("cannot be recovered. Store it somewhere safe.")
    return wallet


def open_existing_wallet(filename: str):
    # Full flow — load encrypted wallet with password
    print(f"\n=== OPEN QTOP WALLET: {filename} ===\n")

    password = getpass.getpass("Enter wallet password: ")

    try:
        wallet = load_wallet(filename, password)
        print(f"\nWallet unlocked successfully.")
        print(f"Address: {wallet['address']}")
        return wallet
    except ValueError as e:
        print(f"\nError: {e}")
        return None


# --- TEST IT ---
if __name__ == "__main__":
    print("=" * 55)
    print("  QTOP WALLET MANAGER TEST")
    print("=" * 55)

    # Create a new encrypted wallet
    wallet = create_new_wallet("test_wallet.qtp")
    print("")

    # Try loading it back with correct password
    print("Testing wallet load with correct password...")
    password  = getpass.getpass("Re-enter your password to test loading: ")
    loaded    = load_wallet("test_wallet.qtp", password)
    keys_match = loaded["private_key"] == wallet["private_key"]
    print(f"Private key matches after decryption: {keys_match}")
    print("")

    # Try loading with wrong password
    print("Testing wrong password detection...")
    try:
        load_wallet("test_wallet.qtp", "wrongpassword123")
        print("ERROR: Should have failed with wrong password")
    except ValueError as e:
        print(f"Correctly rejected wrong password: {e}")

    print("")
    print("=" * 55)
    print("  WALLET ENCRYPTION COMPLETE")
    print("=" * 55)
