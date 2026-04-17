use crate::block::Block;
use crate::transaction::{SignedTransaction, TransactionData};
use crate::wallet::Wallet;

const INITIAL_REWARD: u64      = 5_000_000_000;
const HALVING_INTERVAL: u64    = 210_000;
const TARGET_BLOCK_TIME: u64   = 150;
const ADJUSTMENT_INTERVAL: u64 = 10;

pub struct Blockchain {
    pub chain:      Vec<Block>,
    pub mempool:    Vec<SignedTransaction>,
    pub difficulty: usize,
}

impl Blockchain {
    pub fn new() -> Self {
        let difficulty = 4;
        println!("Initializing QTP blockchain...");
        let genesis = Block::genesis(difficulty);
        Blockchain {
            chain:      vec![genesis],
            mempool:    vec![],
            difficulty,
        }
    }

    pub fn latest_block(&self) -> &Block {
        self.chain.last().unwrap()
    }

    pub fn height(&self) -> u64 {
        self.chain.len() as u64
    }

    pub fn add_transaction(&mut self, tx: SignedTransaction) {
        self.mempool.push(tx);
        self.mempool.sort_by(|a, b| b.data.fee.cmp(&a.data.fee));
        println!(
            "  Transaction added to mempool. Pending: {}",
            self.mempool.len()
        );
    }

    pub fn get_balance(&self, address: &str) -> u64 {
        let mut received: u64 = 0;
        let mut sent: u64     = 0;
        for block in &self.chain {
            for tx in &block.transactions {
                if tx.data.recipient == address {
                    received = received.saturating_add(tx.data.amount);
                }
                if tx.data.sender == address {
                    sent = sent.saturating_add(tx.data.amount);
                    sent = sent.saturating_add(tx.data.fee);
                }
            }
        }
        received.saturating_sub(sent)
    }

    pub fn get_current_reward(&self) -> u64 {
        let halvings = self.height() / HALVING_INTERVAL;
        if halvings >= 64 { return 0; }
        INITIAL_REWARD >> halvings
    }

    pub fn get_total_fees(&self, transactions: &[SignedTransaction]) -> u64 {
        transactions.iter().map(|tx| tx.data.fee).sum()
    }

    pub fn adjust_difficulty(&mut self) {
        let height = self.height();
        if height % ADJUSTMENT_INTERVAL != 0 || height < ADJUSTMENT_INTERVAL {
            return;
        }
        let last_block  = self.latest_block();
        let first_block = &self.chain[(height - ADJUSTMENT_INTERVAL) as usize];
        let actual_time   = last_block.timestamp - first_block.timestamp;
        let expected_time = TARGET_BLOCK_TIME * ADJUSTMENT_INTERVAL;
        if actual_time < expected_time / 2 {
            self.difficulty += 1;
            println!("  Difficulty increased to {} (too fast: {}s vs {}s)",
                self.difficulty, actual_time, expected_time);
        } else if actual_time > expected_time * 2 && self.difficulty > 1 {
            self.difficulty -= 1;
            println!("  Difficulty decreased to {} (too slow: {}s vs {}s)",
                self.difficulty, actual_time, expected_time);
        } else {
            println!("  Difficulty unchanged at {} ({}s vs {}s expected)",
                self.difficulty, actual_time, expected_time);
        }
    }

    pub fn mine_pending_transactions(
        &mut self,
        miner_address: &str,
        miner_wallet:  &Wallet,
    ) {
        self.adjust_difficulty();

        let reward       = self.get_current_reward();
        let fees         = self.get_total_fees(&self.mempool);
        let total_payout = reward + fees;

        let reward_data = TransactionData {
            sender:    "NETWORK".to_string(),
            recipient: miner_address.to_string(),
            amount:    total_payout,
            fee:       0,
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        };

        let signed_reward = crate::transaction::sign_transaction(
            &reward_data,
            &miner_wallet.secret_key,
            &miner_wallet.public_key,
        ).expect("Reward signing failed");

        let mut transactions = vec![signed_reward];
        transactions.extend(self.mempool.drain(..));

        let mut new_block = Block::new(
            self.height(),
            transactions,
            self.latest_block().hash.clone(),
        );

        println!("\nMining block {} at difficulty {}...",
            new_block.index, self.difficulty);
        new_block.mine(self.difficulty);

        println!("  Miner earned {} cori reward + {} cori fees = {} cori total",
            reward, fees, total_payout);

        self.chain.push(new_block);
    }

    pub fn is_valid(&self) -> bool {
        println!("\nValidating blockchain...");
        for i in 1..self.chain.len() {
            let current  = &self.chain[i];
            let previous = &self.chain[i - 1];
            if !current.is_valid() {
                println!("  INVALID: Block {} hash corrupted", i);
                return false;
            }
            if current.previous_hash != previous.hash {
                println!("  INVALID: Block {} disconnected from chain", i);
                return false;
            }
        }
        println!("  Chain valid — {} blocks verified", self.chain.len());
        true
    }
}
