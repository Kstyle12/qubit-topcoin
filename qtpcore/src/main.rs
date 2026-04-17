mod wallet;
mod transaction;

use wallet::Wallet;
use transaction::{TransactionData, sign_transaction, verify_transaction};

fn main() {
    println!("=========================================");
    println!("  QTP CORE NODE (Rust)");
    println!("  Quantum-Resistant. For Everyone. Forever.");
    println!("=========================================");
    println!();

    // --- WALLET TEST ---
    println!("=== WALLET GENERATION ===");
    let sender    = Wallet::new();
    let recipient = Wallet::new();
    println!("Sender:    {}", sender.address);
    println!("Recipient: {}", recipient.address);
    println!();

    // --- TRANSACTION TEST ---
    println!("=== TRANSACTION SIGNING ===");

    // Amount in cori: 10 QTP = 1,000,000,000 cori
    // Fee in cori: 0.001 QTP = 100,000 cori
    let tx_data = TransactionData::new(
        sender.address.clone(),
        recipient.address.clone(),
        1_000_000_000,
        100_000,
    );

    println!("Sending:   {} cori (10 QTP)", tx_data.amount);
    println!("Fee:       {} cori (0.001 QTP)", tx_data.fee);
    println!("Hash:      {}", tx_data.hash());
    println!();

    // Sign with sender's secret key
    println!("Signing with FALCON-512...");
    let signed_tx = sign_transaction(
        &tx_data,
        &sender.secret_key,
        &sender.public_key,
    ).expect("Signing failed");

    println!("Signature: {}...", &signed_tx.signature[..40]);
    println!();

    // Verify
    println!("=== VERIFICATION ===");
    let valid = verify_transaction(&signed_tx);
    println!("Signature valid: {}", valid);

    // Tamper test
    println!();
    println!("=== TAMPER DETECTION ===");
    let mut tampered = signed_tx.clone();
    tampered.data.amount = 999_999_999_999;
    let tampered_valid = verify_transaction(&tampered);
    println!("Tampered valid:  {}", tampered_valid);
    println!();

    if valid && !tampered_valid {
        println!("✓ FALCON-512 transaction security confirmed");
        println!("✓ Tamper detection working perfectly");
    }

    println!();
    println!("=========================================");
}
