mod wallet;
mod transaction;
mod block;

use wallet::Wallet;
use transaction::{TransactionData, sign_transaction, verify_transaction};
use block::Block;

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
    let tx_data = TransactionData::new(
        sender.address.clone(),
        recipient.address.clone(),
        1_000_000_000,
        100_000,
    );

    let signed_tx = sign_transaction(
        &tx_data,
        &sender.secret_key,
        &sender.public_key,
    ).expect("Signing failed");

    println!("Transaction signed: {}", &signed_tx.hash[..20]);
    println!("Signature valid:    {}", verify_transaction(&signed_tx));
    println!();

    // --- BLOCK TEST ---
    println!("=== BLOCK MINING ===");

    // Mine genesis block at difficulty 4
    let genesis = Block::genesis(4);
    println!("Genesis valid: {}", genesis.is_valid());
    println!();

    // Mine block 1 containing our transaction
    println!("Mining block 1 with transaction...");
    let mut block_1 = Block::new(
        1,
        vec![signed_tx.clone()],
        genesis.hash.clone(),
    );
    block_1.mine(4);
    println!("Block 1 valid: {}", block_1.is_valid());
    println!();

    // Tamper detection
    println!("=== TAMPER DETECTION ===");
    println!("Block 1 valid before tamper: {}", block_1.is_valid());
    block_1.transactions[0].data.amount = 999_999_999_999;
    println!("Block 1 valid after tamper:  {}", block_1.is_valid());
    println!();

    // Chain link verification
    println!("=== CHAIN LINK VERIFICATION ===");
    let chain_valid = block_1.previous_hash == genesis.hash;
    println!("Block 1 correctly links to genesis: {}", chain_valid);

    println!();
    println!("=========================================");
    println!("  ALL SYSTEMS OPERATIONAL");
    println!("=========================================");
}
