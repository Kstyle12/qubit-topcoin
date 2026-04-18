use pqcrypto_falcon::falcon512;
use pqcrypto_traits::sign::{PublicKey, SecretKey, SignedMessage};
use sha3::{Digest, Sha3_256};

fn generate_address(public_key: &[u8]) -> String {
    let mut hasher = Sha3_256::new();
    hasher.update(public_key);
    let hash          = hasher.finalize();
    let address_bytes = &hash[hash.len() - 20..];
    let mut versioned = vec![0x26u8];
    versioned.extend_from_slice(address_bytes);
    let mut h2 = Sha3_256::new();
    h2.update(&versioned);
    let first_hash = h2.finalize();
    let mut h3 = Sha3_256::new();
    h3.update(&first_hash);
    let second_hash = h3.finalize();
    let mut full = versioned.clone();
    full.extend_from_slice(&second_hash[..4]);
    bs58::encode(&full).into_string()
}

fn main() {
    println!("Generating sender wallet...");
    let (sender_pk, sender_sk) = falcon512::keypair();
    let sender_address = generate_address(sender_pk.as_bytes());
    println!("Sender: {}", sender_address);

    println!("Generating recipient wallet...");
    let (recipient_pk, _) = falcon512::keypair();
    let recipient_address = generate_address(recipient_pk.as_bytes());
    println!("Recipient: {}", recipient_address);

    let timestamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs();

    let amount: u64 = 1_000_000_000;
    let fee: u64    = 100_000;

    let tx_string = format!(
        "{}:{}:{}:{}:{}",
        sender_address, recipient_address, amount, fee, timestamp
    );

    let signed_msg = falcon512::sign(tx_string.as_bytes(), &sender_sk);
    let sig_hex    = hex::encode(signed_msg.as_bytes());
    let pk_hex     = hex::encode(sender_pk.as_bytes());

    let payload = serde_json::json!({
        "sender":     sender_address,
        "recipient":  recipient_address,
        "amount":     amount,
        "fee":        fee,
        "timestamp":  timestamp,
        "signature":  sig_hex,
        "public_key": pk_hex
    });

    println!("\nSubmitting transaction to Rust node...");
    let client   = reqwest::blocking::Client::new();
    let response = client
        .post("http://localhost:5003/transactions/new")
        .json(&payload)
        .send()
        .expect("Failed to connect to node");

    println!("Status: {}", response.status());
    println!("Response: {}", response.text().unwrap());
}
