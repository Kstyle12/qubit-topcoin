
fn register_miner(node_url: &str, address: &str) -> bool {
    let url    = format!("{}/set_miner/{}", node_url, address);
    let client = reqwest::blocking::Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .build()
        .unwrap();
    match client.post(&url).send() {
        Ok(r)  => r.status().is_success(),
        Err(_) => false,
    }
}

// =========================================
//   QTP — Qubit TopCoin CPU Miner
//   Cori Testnet
//   Quantum-Resistant. For Everyone. Forever.
// =========================================

use std::time::{Duration, Instant};
use std::thread;

const NODE_URL:       &str = "http://localhost:5003";
const POLL_INTERVAL:  u64  = 5; // seconds between checks

fn print_header() {
    println!("");
    println!("=========================================");
    println!("  QTP CPU MINER");
    println!("  Quantum-Resistant. For Everyone. Forever.");
    println!("  Network: Cori Testnet");
    println!("=========================================");
    println!("");
}

fn get_status(node_url: &str) -> Option<serde_json::Value> {
    let url    = format!("{}/status", node_url);
    let client = reqwest::blocking::Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .build()
        .unwrap();
    match client.get(&url).send() {
        Ok(r)  => r.json().ok(),
        Err(_) => None,
    }
}

fn mine_block(node_url: &str, _miner_address: &str) -> Option<serde_json::Value> {
    let url    = format!("{}/mine", node_url);
    let client = reqwest::blocking::Client::builder()
        .timeout(std::time::Duration::from_secs(300)) // 5 min timeout for mining
        .build()
        .unwrap();
    match client.get(&url).send() {
        Ok(r)  => r.json().ok(),
        Err(_) => None,
    }
}

fn get_balance(node_url: &str, address: &str) -> u64 {
    let url = format!("{}/balance/{}", node_url, address);
    match reqwest::blocking::get(&url) {
        Ok(r) => {
            if let Ok(data) = r.json::<serde_json::Value>() {
                data["balance"].as_u64().unwrap_or(0)
            } else {
                0
            }
        }
        Err(_) => 0,
    }
}

fn timestamp() -> String {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs();

    let hours   = (now % 86400) / 3600;
    let minutes = (now % 3600) / 60;
    let seconds = now % 60;
    format!("{:02}:{:02}:{:02}", hours, minutes, seconds)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();

    // Get miner address from args or prompt
    let miner_address = if args.len() > 1 {
        args[1].clone()
    } else {
        println!("Usage: miner <your_qtp_address> [node_url]");
        println!("Example: miner GRgnXA7g5fz58EU58nriyuUq4FwkxhL3vQ");
        println!("");
        print!("Enter your QTP wallet address: ");
        use std::io::Write;
        std::io::stdout().flush().unwrap();
        let mut input = String::new();
        std::io::stdin().read_line(&mut input).unwrap();
        input.trim().to_string()
    };

    if miner_address.is_empty() {
        println!("No address provided. Exiting.");
        return;
    }

    let node_url = if args.len() > 2 {
        args[2].clone()
    } else {
        NODE_URL.to_string()
    };

    print_header();
    println!("Mining to:  {}", miner_address);
    println!("Node:       {}", node_url);
    println!("Press Ctrl+C to stop");
    println!("-----------------------------------------");
    println!("");

    // Check node is reachable
    print!("Connecting to node...");
    match get_status(&node_url) {
        Some(status) => {
            println!(" connected");
            println!(
                "Chain height: {} blocks | Difficulty: {}",
                status["blocks"].as_u64().unwrap_or(0),
                status["difficulty"].as_u64().unwrap_or(0)
            );
        }
        None => {
            println!(" FAILED");
            println!("Cannot reach node at {}", node_url);
            println!("Make sure your node is running.");
            return;
        }
    }

    // Register miner address with node
    print!("Registering miner address...");
    if register_miner(&node_url, &miner_address) {
        println!(" done");
    } else {
        println!(" failed (node may not support this yet)");
    }

    println!("");

    // Mining loop
    let mut blocks_mined:  u64   = 0;
    let mut total_earned:  u64   = 0;
    let start_time               = Instant::now();

    loop {
        // Check for pending transactions
        match get_status(&node_url) {
            Some(status) => {
                let pending = status["pending_txs"].as_u64().unwrap_or(0);
                let height  = status["blocks"].as_u64().unwrap_or(0);

                if pending == 0 {
                    println!(
                        "[{}] Waiting for transactions... (height: {})",
                        timestamp(), height
                    );
                    thread::sleep(Duration::from_secs(POLL_INTERVAL));
                    continue;
                }

                println!(
                    "[{}] {} pending transaction(s) found. Mining...",
                    timestamp(), pending
                );

                // Mine the block
                let mine_start = Instant::now();
                match mine_block(&node_url, &miner_address) {
                    Some(result) => {
                        if result.get("hash").is_some() {
                            blocks_mined += 1;

                            let reward = result["reward"].as_u64()
                                .unwrap_or(5_000_000_000);
                            total_earned += reward;

                            let elapsed    = mine_start.elapsed();
                            let total_time = start_time.elapsed();

                            println!("[{}] ✓ Block mined!", timestamp());
                            println!(
                                "  Hash:         {}",
                                result["hash"].as_str().unwrap_or("unknown")
                            );
                            println!(
                                "  Miner:        {}",
                                &miner_address[..20]
                            );
                            println!(
                                "  Time:         {:.1}s",
                                elapsed.as_secs_f64()
                            );
                            println!(
                                "  Reward:       {:.8} QTP",
                                reward as f64 / 100_000_000.0
                            );
                            println!(
                                "  Blocks mined: {}",
                                blocks_mined
                            );
                            println!(
                                "  Total earned: {:.8} QTP",
                                total_earned as f64 / 100_000_000.0
                            );
                            println!(
                                "  Mining time:  {:.0}s total",
                                total_time.as_secs_f64()
                            );

                            // Check actual wallet balance
                            let balance = get_balance(&node_url, &miner_address);
                            println!(
                                "  Wallet:       {:.8} QTP",
                                balance as f64 / 100_000_000.0
                            );
                            println!("-----------------------------------------");
                        } else {
                            println!(
                                "[{}] {}",
                                timestamp(),
                                result["message"].as_str().unwrap_or("No transactions")
                            );
                        }
                    }
                    None => {
                        println!(
                            "[{}] Mining error — node unreachable",
                            timestamp()
                        );
                    }
                }
            }
            None => {
                println!(
                    "[{}] Node offline. Retrying in {}s...",
                    timestamp(), POLL_INTERVAL
                );
            }
        }

        thread::sleep(Duration::from_secs(POLL_INTERVAL));
    }
}
