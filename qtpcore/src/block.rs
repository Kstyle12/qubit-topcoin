use sha3::{Digest, Sha3_256};
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use crate::transaction::{SignedTransaction, verify_transaction};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Block {
    pub index:         u64,
    pub timestamp:     u64,
    pub transactions:  Vec<SignedTransaction>,
    pub previous_hash: String,
    pub nonce:         u64,
    pub hash:          String,
}

impl Block {
    pub fn new(
        index:         u64,
        transactions:  Vec<SignedTransaction>,
        previous_hash: String,
    ) -> Self {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let mut block = Block {
            index,
            timestamp,
            transactions,
            previous_hash,
            nonce: 0,
            hash: String::new(),
        };

        block.hash = block.calculate_hash();
        block
    }

    pub fn calculate_hash(&self) -> String {
        let contents = format!(
            "{}:{}:{}:{}:{}",
            self.index,
            self.timestamp,
            self.previous_hash,
            self.nonce,
            self.transactions_hash()
        );

        let mut hasher = Sha3_256::new();
        hasher.update(contents.as_bytes());
        hex::encode(hasher.finalize())
    }

    pub fn transactions_hash(&self) -> String {
        // Hash all transaction hashes together
        // If any transaction data changes, this changes
        // which changes the block hash
        let mut hasher = Sha3_256::new();
        for tx in &self.transactions {
            // Use the full transaction data hash not just tx.hash
            // so tampering with amount is caught here
            let tx_bytes = format!(
                "{}:{}:{}:{}:{}",
                tx.data.sender,
                tx.data.recipient,
                tx.data.amount,
                tx.data.fee,
                tx.data.timestamp
            );
            hasher.update(tx_bytes.as_bytes());
        }
        hex::encode(hasher.finalize())
    }

    pub fn mine(&mut self, difficulty: usize) {
        let target    = "0".repeat(difficulty);
        let mut attempts: u64 = 0;

        println!("  Mining block {}...", self.index);

        while !self.hash.starts_with(&target) {
            self.nonce += 1;
            self.hash   = self.calculate_hash();
            attempts   += 1;
        }

        println!("  Block {} mined in {} attempts", self.index, attempts);
        println!("  Hash: {}", self.hash);
    }

    pub fn is_valid(&self) -> bool {
        // Check 1: Block hash matches fresh calculation
        // This catches any field tampering including transactions
        if self.hash != self.calculate_hash() {
            return false;
        }

        // Check 2: All transaction signatures are valid
        // This catches transaction data tampering at the crypto level
        for tx in &self.transactions {
            if !verify_transaction(tx) {
                return false;
            }
        }

        true
    }

    pub fn genesis(difficulty: usize) -> Self {
        println!("Creating QTP genesis block...");

        let mut genesis = Block {
            index:         0,
            timestamp:     1700000000,
            transactions:  vec![],
            previous_hash: "0".repeat(64),
            nonce:         0,
            hash:          String::new(),
        };

        genesis.hash = genesis.calculate_hash();
        genesis.mine(difficulty);
        genesis
    }
}
