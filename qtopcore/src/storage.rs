use std::fs;
use std::path::Path;
use crate::block::Block;

const CHAIN_FILE: &str = "qtop_chain.json";

pub fn save_chain(chain: &Vec<Block>) {
    match serde_json::to_string_pretty(chain) {
        Ok(json) => {
            match fs::write(CHAIN_FILE, json) {
                Ok(_)  => println!("  Chain saved to {}", CHAIN_FILE),
                Err(e) => println!("  Failed to save chain: {}", e),
            }
        }
        Err(e) => println!("  Failed to serialize chain: {}", e),
    }
}

pub fn load_chain() -> Option<Vec<Block>> {
    if !Path::new(CHAIN_FILE).exists() {
        println!("  No existing chain found. Starting fresh.");
        return None;
    }
    match fs::read_to_string(CHAIN_FILE) {
        Ok(json) => {
            match serde_json::from_str(&json) {
                Ok(chain) => {
                    println!("  Chain loaded from {}", CHAIN_FILE);
                    Some(chain)
                }
                Err(e) => {
                    println!("  Failed to deserialize chain: {}", e);
                    None
                }
            }
        }
        Err(e) => {
            println!("  Failed to read chain file: {}", e);
            None
        }
    }
}
