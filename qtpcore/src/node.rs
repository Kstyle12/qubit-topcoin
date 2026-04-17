use actix_web::{web, App, HttpServer, HttpResponse, middleware};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use crate::blockchain::Blockchain;
use crate::wallet::Wallet;
use crate::transaction::{TransactionData, SignedTransaction, sign_transaction, verify_transaction};

// Shared state — the blockchain protected by a mutex
// so multiple requests can't corrupt it simultaneously
pub struct NodeState {
    pub chain:         Blockchain,
    pub peers:         Vec<String>,
    pub miner_wallet:  Wallet,
}

// Request/response types
#[derive(Serialize, Deserialize)]
pub struct TransactionRequest {
    pub sender:     String,
    pub recipient:  String,
    pub amount:     u64,
    pub fee:        u64,
    pub timestamp:  u64,
    pub signature:  String,
    pub public_key: String,
}

#[derive(Serialize, Deserialize)]
pub struct PeerRequest {
    pub peer: String,
}

#[derive(Serialize)]
pub struct StatusResponse {
    pub status:      String,
    pub blocks:      u64,
    pub pending_txs: usize,
    pub peers:       Vec<String>,
    pub latest_hash: String,
    pub difficulty:  usize,
}

#[derive(Serialize)]
pub struct BalanceResponse {
    pub address: String,
    pub balance: u64,
    pub qtp:     f64,
}

// GET /status
async fn get_status(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    let node = state.lock().unwrap();
    let latest = node.chain.latest_block();

    HttpResponse::Ok().json(StatusResponse {
        status:      "running".to_string(),
        blocks:      node.chain.height(),
        pending_txs: node.chain.mempool.len(),
        peers:       node.peers.clone(),
        latest_hash: format!("{}...", &latest.hash[..20]),
        difficulty:  node.chain.difficulty,
    })
}

// GET /chain
async fn get_chain(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    let node = state.lock().unwrap();
    HttpResponse::Ok().json(&node.chain.chain)
}

// GET /mine
async fn mine(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    let mut node = state.lock().unwrap();

    if node.chain.mempool.is_empty() {
        return HttpResponse::Ok().json(
            serde_json::json!({"message": "No pending transactions"})
        );
    }

    let miner_address = node.miner_wallet.address.clone();
    let miner_wallet  = Wallet::new(); // Fresh wallet ref for signing

    node.chain.mine_pending_transactions(&miner_address, &miner_wallet);

    let latest = node.chain.latest_block();
    HttpResponse::Ok().json(serde_json::json!({
        "message": format!("Block {} mined", latest.index),
        "hash":    latest.hash.clone(),
        "height":  node.chain.height(),
        "reward":  node.chain.get_current_reward(),
    }))
}

// POST /transactions/new
async fn new_transaction(
    state: web::Data<Mutex<NodeState>>,
    body:  web::Json<TransactionRequest>,
) -> HttpResponse {
    // Reconstruct signed transaction for verification
    let tx_data = TransactionData {
        sender:    body.sender.clone(),
        recipient: body.recipient.clone(),
        amount:    body.amount,
        fee:       body.fee,
        timestamp: body.timestamp,
    };

    let signed_tx = SignedTransaction {
        data:       tx_data.clone(),
        hash:       tx_data.hash(),
        signature:  body.signature.clone(),
        public_key: body.public_key.clone(),
    };

    // Verify FALCON-512 signature
    if !verify_transaction(&signed_tx) {
        return HttpResponse::BadRequest().json(
            serde_json::json!({"error": "Invalid signature — transaction rejected"})
        );
    }

    let mut node = state.lock().unwrap();
    node.chain.add_transaction(signed_tx);

    HttpResponse::Ok().json(
        serde_json::json!({"message": "Transaction added to mempool"})
    )
}

// GET /balance/{address}
async fn get_balance(
    state:   web::Data<Mutex<NodeState>>,
    address: web::Path<String>,
) -> HttpResponse {
    let node    = state.lock().unwrap();
    let balance = node.chain.get_balance(&address);

    HttpResponse::Ok().json(BalanceResponse {
        address: address.to_string(),
        balance,
        qtp: balance as f64 / 100_000_000.0,
    })
}

// POST /peers/register
async fn register_peer(
    state: web::Data<Mutex<NodeState>>,
    body:  web::Json<PeerRequest>,
) -> HttpResponse {
    let mut node = state.lock().unwrap();

    if !node.peers.contains(&body.peer) {
        node.peers.push(body.peer.clone());
    }

    HttpResponse::Ok().json(serde_json::json!({
        "message": format!("Peer {} registered", body.peer),
        "peers":   node.peers.clone(),
    }))
}

// GET /peers/sync  
async fn sync_peers(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    // In production this would fetch chains from all peers
    // and replace with longest valid chain
    let node = state.lock().unwrap();
    HttpResponse::Ok().json(serde_json::json!({
        "message": "Sync complete",
        "blocks":  node.chain.height(),
    }))
}

pub async fn start_node(port: u16) -> std::io::Result<()> {
    println!("=========================================");
    println!("  QTP NODE STARTING ON PORT {}", port);
    println!("=========================================");
    println!("  GET  /status");
    println!("  GET  /chain");
    println!("  GET  /mine");
    println!("  GET  /balance/{{address}}");
    println!("  POST /transactions/new");
    println!("  POST /peers/register");
    println!("  GET  /peers/sync");
    println!("=========================================");

    let state = web::Data::new(Mutex::new(NodeState {
        chain:        Blockchain::new(),
        peers:        vec![],
        miner_wallet: Wallet::new(),
    }));

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/status",            web::get().to(get_status))
            .route("/chain",             web::get().to(get_chain))
            .route("/mine",              web::get().to(mine))
            .route("/balance/{address}", web::get().to(get_balance))
            .route("/transactions/new",  web::post().to(new_transaction))
            .route("/peers/register",    web::post().to(register_peer))
            .route("/peers/sync",        web::get().to(sync_peers))
    })
    .bind(format!("0.0.0.0:{}", port))?
    .run()
    .await
}
