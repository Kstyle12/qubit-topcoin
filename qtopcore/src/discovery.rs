use std::net::ToSocketAddrs;

// DNS seed hostnames — update these when cloud servers are deployed
// These resolve to IP addresses of known QTOP seed nodes
const DNS_SEEDS: &[&str] = &[
    "seed1.qubittopcoin.org",
    "seed2.qubittopcoin.org",
    "seed.cori-testnet.org",
];

// Fallback hardcoded peers if DNS seeds are unreachable
// Update with real IPs when cloud nodes are deployed
const FALLBACK_PEERS: &[&str] = &[
    // "http://1.2.3.4:5003",  // Add real IPs here when available
];

const DEFAULT_PORT: u16 = 5003;

pub fn discover_peers() -> Vec<String> {
    let mut peers = Vec::new();

    println!("  Discovering peers...");

    // Try DNS seeds first
    for seed in DNS_SEEDS {
        let addr = format!("{}:{}", seed, DEFAULT_PORT);
        match addr.to_socket_addrs() {
            Ok(addrs) => {
                for socket_addr in addrs {
                    let peer = format!("http://{}:{}", socket_addr.ip(), DEFAULT_PORT);
                    if !peers.contains(&peer) {
                        println!("  Found peer via DNS: {}", peer);
                        peers.push(peer);
                    }
                }
            }
            Err(_) => {
                // DNS seed unreachable — normal during early testnet
            }
        }
    }

    // Add fallback peers if DNS found nothing
    if peers.is_empty() {
        for peer in FALLBACK_PEERS {
            peers.push(peer.to_string());
        }
        if !FALLBACK_PEERS.is_empty() {
            println!("  Using fallback peers");
        } else {
            println!("  No peers found — running as bootstrap node");
        }
    }

    println!("  Discovered {} peer(s)", peers.len());
    peers
}

pub fn is_reachable(peer: &str) -> bool {
    // Quick check if a peer is actually responding
    let url = format!("{}/status", peer);
    match reqwest::blocking::get(&url) {
        Ok(r)  => r.status().is_success(),
        Err(_) => false,
    }
}

pub fn filter_reachable(peers: Vec<String>) -> Vec<String> {
    peers
        .into_iter()
        .filter(|p| is_reachable(p))
        .collect()
}
