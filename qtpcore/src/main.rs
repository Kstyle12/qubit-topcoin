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
    let port: u16 = env::args()
        .nth(1)
        .and_then(|p| p.parse().ok())
        .unwrap_or(5003);

    node::start_node(port).await.expect("Node failed to start");
}
