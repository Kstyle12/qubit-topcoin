mod wallet;
mod transaction;
mod randomx;
mod block;
mod storage;
mod blockchain;
mod sync;
mod identity;
mod discovery;
mod node;

use std::env;

#[actix_web::main]
async fn main() {
    let args: Vec<String> = env::args().collect();

    let port: u16 = args.get(1)
        .and_then(|p| p.parse().ok())
        .unwrap_or(5003);

    // Optional miner address as second argument
    // cargo run --bin qtpcore -- 5003 GNKoG6N5adR7zoVqNBtMqfPVaQSdG48XXY
    let miner_addr = args.get(2).cloned();

    if let Some(ref addr) = miner_addr {
        println!("Miner address: {}", addr);
    }

    node::start_node(port, miner_addr).await.expect("Node failed to start");
}
