mod wallet;
mod transaction;
mod block;
mod blockchain;

use wallet::Wallet;
use transaction::{TransactionData, sign_transaction};
use blockchain::Blockchain;

fn main() {
    println!("=========================================");
    println!("  QTP CORE NODE (Rust)");
    println!("  Quantum-Resistant. For Everyone. Forever.");
    println!("=========================================");
    println!();

    println!("=== GENERATING WALLETS ===");
    let miner     = Wallet::new();
    let sender    = Wallet::new();
    let recipient = Wallet::new();
    println!("Miner:     {}", miner.address);
    println!("Sender:    {}", sender.address);
    println!("Recipient: {}", recipient.address);
    println!();

    println!("=== INITIALIZING BLOCKCHAIN ===");
    let mut chain = Blockchain::new();
    println!("Genesis block created. Height: {}", chain.height());
    println!();

    println!("=== CREATING TRANSACTION ===");
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
    println!("Transaction signed: {}...", &signed_tx.hash[..20]);
    chain.add_transaction(signed_tx);
    println!();

    println!("=== MINING BLOCK 1 ===");
    chain.mine_pending_transactions(&miner.address, &miner);
    println!("Chain height: {}", chain.height());
    println!();

    println!("=== BALANCES ===");
    let miner_bal     = chain.get_balance(&miner.address);
    let sender_bal    = chain.get_balance(&sender.address);
    let recipient_bal = chain.get_balance(&recipient.address);
    println!("Miner:     {} cori ({:.8} QTP)",
        miner_bal, miner_bal as f64 / 100_000_000.0);
    println!("Sender:    {} cori ({:.8} QTP)",
        sender_bal, sender_bal as f64 / 100_000_000.0);
    println!("Recipient: {} cori ({:.8} QTP)",
        recipient_bal, recipient_bal as f64 / 100_000_000.0);
    println!();

    println!("=== CHAIN VALIDATION ===");
    let valid = chain.is_valid();
    println!("Chain valid: {}", valid);
    println!();

    println!("=== TAMPER DETECTION ===");
    chain.chain[1].transactions[0].data.amount = 999_999_999_999;
    let valid_after = chain.is_valid();
    println!("Chain valid after tamper: {}", valid_after);

    println!();
    println!("=========================================");
    println!("  BLOCKCHAIN COMPLETE");
    println!("=========================================");
}
