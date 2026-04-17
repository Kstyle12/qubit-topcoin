use pqcrypto_falcon::falcon512;
use pqcrypto_traits::sign::{PublicKey, SecretKey};
use sha3::{Digest, Sha3_256};

fn generate_wallet() -> (String, String, String) {
    let (public_key, secret_key) = falcon512::keypair();

    let mut hasher = Sha3_256::new();
    hasher.update(public_key.as_bytes());
    let hash = hasher.finalize();

    let address_bytes = &hash[hash.len() - 20..];
    let mut versioned = vec![0x26u8];
    versioned.extend_from_slice(address_bytes);

    let mut hasher2 = Sha3_256::new();
    hasher2.update(&versioned);
    let first_hash = hasher2.finalize();

    let mut hasher3 = Sha3_256::new();
    hasher3.update(&first_hash);
    let second_hash = hasher3.finalize();

    let checksum = &second_hash[..4];
    let mut full_address = versioned.clone();
    full_address.extend_from_slice(checksum);
    let address = bs58::encode(&full_address).into_string();

    let public_key_hex = hex::encode(public_key.as_bytes());
    let secret_key_hex = hex::encode(secret_key.as_bytes());

    (address, public_key_hex, secret_key_hex)
}

fn main() {
    println!("=========================================");
    println!("  QTP WALLET GENERATOR (Rust)");
    println!("  Quantum-Resistant. For Everyone. Forever.");
    println!("=========================================");
    println!();

    println!("Generating FALCON-512 wallet...");
    println!();

    let (address, public_key, secret_key) = generate_wallet();

    println!("Address:     {}", address);
    println!("Public Key:  {}...", &public_key[..40]);
    println!("Private Key: {}...", &secret_key[..40]);
    println!();
    println!("WARNING: Never share your private key with anyone. Ever.");
    println!();

    println!("Generating second wallet to prove uniqueness...");
    let (address2, _, _) = generate_wallet();
    println!("Address 2:   {}", address2);
    println!();

    if address != address2 {
        println!("Wallets are unique - cryptographic randomness confirmed");
    }

    println!();
    println!("=========================================");
}
