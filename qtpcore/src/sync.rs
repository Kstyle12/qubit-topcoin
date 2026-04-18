use crate::block::Block;
use crate::blockchain::Blockchain;
use crate::storage::save_chain;

pub fn sync_with_peers(chain: &mut Blockchain, peers: &[String]) -> bool {
    let mut longest_chain: Option<Vec<Block>> = None;
    let mut max_length = chain.height() as usize;

    for peer in peers {
        let url = format!("{}/chain", peer);

        // Use a separate thread for blocking HTTP call
        let url_clone = url.clone();
        let result = std::thread::spawn(move || {
            reqwest::blocking::get(&url_clone)
                .ok()
                .and_then(|r| r.json::<Vec<Block>>().ok())
        }).join();

        if let Ok(Some(peer_chain)) = result {
            let peer_length = peer_chain.len();
            println!("  Peer {} has {} blocks", peer, peer_length);

            if peer_length > max_length && is_valid_chain(&peer_chain) {
                max_length    = peer_length;
                longest_chain = Some(peer_chain);
            }
        } else {
            println!("  Could not reach peer {}", peer);
        }
    }

    if let Some(new_chain) = longest_chain {
        println!("  Replacing chain with longer peer chain ({} blocks)", max_length);
        chain.chain   = new_chain;
        chain.mempool = vec![];
        save_chain(&chain.chain);
        return true;
    }

    println!("  Our chain is already the longest ({} blocks)", chain.height());
    false
}

fn is_valid_chain(chain: &[Block]) -> bool {
    for i in 1..chain.len() {
        let current  = &chain[i];
        let previous = &chain[i - 1];
        if !current.is_valid() {
            return false;
        }
        if current.previous_hash != previous.hash {
            return false;
        }
    }
    true
}
