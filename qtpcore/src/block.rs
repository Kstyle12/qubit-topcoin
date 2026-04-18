use sha3::{Digest, Sha3_256};
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use crate::transaction::{SignedTransaction, verify_transaction};
use crate::randomx::{RandomXHasher, meets_difficulty};

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
        // Use SHA3 for block identification
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
        let mut hasher = Sha3_256::new();
        for tx in &self.transactions {
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
        println!("  Mining block {} with RandomX...", self.index);

        // RandomX key is the previous block hash
        // This changes every block making ASICs ineffective
        let rx_key  = self.previous_hash.as_bytes();
        let hasher  = RandomXHasher::new(rx_key);
        let mut attempts: u64 = 0;

        loop {
            self.nonce += 1;
            self.hash   = self.calculate_hash();

            // Use RandomX to hash the block header
            let rx_input  = self.hash.as_bytes();
            let rx_hash   = hasher.hash(rx_input);
            let rx_hex    = hex::encode(rx_hash);

            attempts += 1;

            if meets_difficulty(&rx_hash, difficulty) {
                // Store the RandomX hash as the final block hash
                self.hash = rx_hex;
                println!(
                    "  Block {} mined with RandomX in {} attempts",
                    self.index, attempts
                );
                println!("  Hash: {}", self.hash);
                break;
            }
        }
    }

    pub fn is_valid(&self) -> bool {
        // Verify all transaction signatures
        for tx in &self.transactions {
            if tx.data.sender != "NETWORK" && tx.data.sender != "GENESIS" {
                if !verify_transaction(tx) {
                    return false;
                }
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
