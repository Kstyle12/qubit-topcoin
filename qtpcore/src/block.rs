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
    pub hash:          String,  // RandomX hash — proof of work
    pub header_hash:   String,  // SHA-3 hash — block identifier
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
            nonce:       0,
            hash:        String::new(),
            header_hash: String::new(),
        };

        block.header_hash = block.calculate_header_hash();
        block.hash        = block.header_hash.clone();
        block
    }

    pub fn calculate_header_hash(&self) -> String {
        // SHA-3 hash of block contents — used as block identifier
        // and as input to RandomX
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

        // RandomX key changes every block based on previous hash
        // This makes it impossible for ASICs to pre-compute solutions
        let rx_key   = self.previous_hash.as_bytes().to_vec();
        let hasher   = RandomXHasher::new(&rx_key);
        let mut attempts: u64 = 0;

        loop {
            self.nonce       += 1;
            self.header_hash  = self.calculate_header_hash();

            // Feed SHA-3 header hash into RandomX
            let rx_hash = hasher.hash(self.header_hash.as_bytes());

            attempts += 1;

            if meets_difficulty(&rx_hash, difficulty) {
                // Store RandomX hash as the proof of work
                self.hash = hex::encode(rx_hash);
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
        // Check 1: Header hash is correct
        if self.header_hash != self.calculate_header_hash() {
            return false;
        }

        // Check 2: All transaction signatures are valid
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
            header_hash:   String::new(),
        };

        genesis.header_hash = genesis.calculate_header_hash();
        genesis.hash        = genesis.header_hash.clone();
        genesis.mine(difficulty);
        genesis
    }
}
