mod wallet;
mod transaction;
mod block;
mod blockchain;
mod node;

use std::env;

#[actix_web::main]
async fn main() {
    // Get port from command line argument
    // cargo run -- 5000
    let port: u16 = env::args()
        .nth(1)
        .and_then(|p| p.parse().ok())
        .unwrap_or(5000);

    node::start_node(port).await.expect("Node failed to start");
}
