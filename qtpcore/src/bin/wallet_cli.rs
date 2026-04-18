use pqcrypto_falcon::falcon512;
use pqcrypto_traits::sign::{PublicKey, SecretKey, SignedMessage};
use sha3::{Digest, Sha3_256};
use serde::{Deserialize, Serialize};
use std::io::{self, Write};
use std::fs;
use std::path::Path;

const NODE_URL: &str = "http://localhost:5003";

// --- WALLET FILE STRUCTURE ---
#[derive(Serialize, Deserialize)]
struct WalletFile {
    version:    String,
    address:    String,
    public_key: String,
    secret_key: String, // In production this would be encrypted
}

// --- WALLET GENERATION ---
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

fn create_wallet(filename: &str) {
    println!("\n=== CREATE NEW QTP WALLET ===\n");

    if Path::new(filename).exists() {
        print!("Wallet file {} already exists. Overwrite? (yes/no): ", filename);
        io::stdout().flush().unwrap();
        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();
        if input.trim() != "yes" {
            println!("Cancelled.");
            return;
        }
    }

    println!("Generating FALCON-512 keypair...");
    let (public_key, secret_key) = falcon512::keypair();
    let address = generate_address(public_key.as_bytes());

    let wallet = WalletFile {
        version:    "1.0".to_string(),
        address:    address.clone(),
        public_key: hex::encode(public_key.as_bytes()),
        secret_key: hex::encode(secret_key.as_bytes()),
    };

    let json = serde_json::to_string_pretty(&wallet).unwrap();
    fs::write(filename, json).expect("Failed to save wallet");

    println!("\n✓ Wallet created successfully");
    println!("  Address: {}", address);
    println!("  File:    {}", filename);
    println!("\n  WARNING: Keep your wallet file safe.");
    println!("  Anyone with this file can spend your QTP.\n");
}

fn load_wallet(filename: &str) -> Option<WalletFile> {
    if !Path::new(filename).exists() {
        println!("Wallet file {} not found.", filename);
        println!("Create one with: qtpwallet create\n");
        return None;
    }

    let json = fs::read_to_string(filename).expect("Failed to read wallet");
    match serde_json::from_str(&json) {
        Ok(wallet) => Some(wallet),
        Err(e) => {
            println!("Failed to parse wallet file: {}", e);
            None
        }
    }
}

fn check_balance(filename: &str) {
    println!("\n=== CHECK BALANCE ===\n");

    let wallet = match load_wallet(filename) {
        Some(w) => w,
        None    => return,
    };

    println!("Address: {}", wallet.address);
    println!("Node:    {}\n", NODE_URL);

    let url = format!("{}/balance/{}", NODE_URL, wallet.address);
    match reqwest::blocking::get(&url) {
        Ok(response) => {
            match response.json::<serde_json::Value>() {
                Ok(data) => {
                    let balance = data["balance"].as_u64().unwrap_or(0);
                    let qtp     = balance as f64 / 100_000_000.0;
                    println!("✓ Balance: {:.8} QTP", qtp);
                    println!("         {} cori\n", balance);
                }
                Err(_) => println!("Failed to parse balance response\n"),
            }
        }
        Err(_) => {
            println!("✗ Could not connect to node at {}", NODE_URL);
            println!("  Make sure your node is running.\n");
        }
    }
}

fn send_qtp(filename: &str) {
    println!("\n=== SEND QTP ===\n");

    let wallet = match load_wallet(filename) {
        Some(w) => w,
        None    => return,
    };

    println!("Sending from: {}\n", wallet.address);

    // Get recipient
    print!("Recipient address: ");
    io::stdout().flush().unwrap();
    let mut recipient = String::new();
    io::stdin().read_line(&mut recipient).unwrap();
    let recipient = recipient.trim().to_string();

    // Get amount
    print!("Amount (QTP): ");
    io::stdout().flush().unwrap();
    let mut amount_str = String::new();
    io::stdin().read_line(&mut amount_str).unwrap();
    let amount_qtp: f64 = match amount_str.trim().parse() {
        Ok(a)  => a,
        Err(_) => { println!("Invalid amount.\n"); return; }
    };

    // Get fee
    print!("Fee (QTP, default 0.001): ");
    io::stdout().flush().unwrap();
    let mut fee_str = String::new();
    io::stdin().read_line(&mut fee_str).unwrap();
    let fee_qtp: f64 = fee_str.trim().parse().unwrap_or(0.001);

    // Convert to cori
    let amount_cori = (amount_qtp * 100_000_000.0) as u64;
    let fee_cori    = (fee_qtp * 100_000_000.0) as u64;
    let timestamp   = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs();

    // Confirm
    println!("\nYou are about to send:");
    println!("  Amount:    {:.8} QTP", amount_qtp);
    println!("  Fee:       {:.8} QTP", fee_qtp);
    println!("  To:        {}", recipient);
    print!("\nConfirm? (yes/no): ");
    io::stdout().flush().unwrap();
    let mut confirm = String::new();
    io::stdin().read_line(&mut confirm).unwrap();
    if confirm.trim() != "yes" {
        println!("Transaction cancelled.\n");
        return;
    }

    // Sign transaction
    println!("\nSigning with FALCON-512...");
    let tx_string = format!(
        "{}:{}:{}:{}:{}",
        wallet.address, recipient, amount_cori, fee_cori, timestamp
    );

    let sk_bytes = hex::decode(&wallet.secret_key).expect("Invalid secret key");
    let sk       = falcon512::SecretKey::from_bytes(&sk_bytes)
        .expect("Failed to load secret key");

    let signed_msg = falcon512::sign(tx_string.as_bytes(), &sk);
    let sig_hex    = hex::encode(signed_msg.as_bytes());

    // Submit to node
    let payload = serde_json::json!({
        "sender":     wallet.address,
        "recipient":  recipient,
        "amount":     amount_cori,
        "fee":        fee_cori,
        "timestamp":  timestamp,
        "signature":  sig_hex,
        "public_key": wallet.public_key
    });

    let client = reqwest::blocking::Client::new();
    match client
        .post(format!("{}/transactions/new", NODE_URL))
        .json(&payload)
        .send()
    {
        Ok(response) => {
            if response.status().is_success() {
                println!("✓ Transaction submitted to network");
                println!("  It will be confirmed in the next mined block.\n");
            } else {
                println!("✗ Transaction rejected: {}\n", response.text().unwrap());
            }
        }
        Err(_) => println!("✗ Could not connect to node.\n"),
    }
}

fn show_help() {
    println!("\n=== QTP WALLET CLI ===");
    println!("Quantum-Resistant. For Everyone. Forever.\n");
    println!("Usage:");
    println!("  qtpwallet create              Create a new wallet");
    println!("  qtpwallet balance             Check wallet balance");
    println!("  qtpwallet send                Send QTP");
    println!("  qtpwallet address             Show wallet address");
    println!("  qtpwallet help                Show this help\n");
    println!("Default wallet file: wallet.qtp");
    println!("Default node:        {}\n", NODE_URL);
}

fn show_address(filename: &str) {
    if let Some(wallet) = load_wallet(filename) {
        println!("\nAddress: {}\n", wallet.address);
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let command  = args.get(1).map(|s| s.as_str()).unwrap_or("help");
    let filename = args.get(2).map(|s| s.as_str()).unwrap_or("wallet.qtp");

    match command {
        "create"  => create_wallet(filename),
        "balance" => check_balance(filename),
        "send"    => send_qtp(filename),
        "address" => show_address(filename),
        _         => show_help(),
    }
}
