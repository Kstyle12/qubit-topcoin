use actix_web::{web, App, HttpServer, HttpResponse};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use crate::blockchain::Blockchain;
use crate::wallet::Wallet;
use crate::transaction::{TransactionData, SignedTransaction, verify_transaction, verify_detached};
use crate::sync::sync_with_peers;

pub struct NodeState {
    pub chain:        Blockchain,
    pub peers:        Vec<String>,
    pub miner_wallet: Wallet,
}

#[derive(Serialize, Deserialize, Clone)]
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

async fn get_status(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    let node   = state.lock().unwrap();
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

async fn get_chain(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    let node = state.lock().unwrap();
    HttpResponse::Ok().json(&node.chain.chain)
}

async fn mine(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    let mut node = state.lock().unwrap();

    if node.chain.mempool.is_empty() {
        return HttpResponse::Ok().json(
            serde_json::json!({"message": "No pending transactions"})
        );
    }

    let miner_address = node.miner_wallet.address.clone();
    let miner_wallet  = Wallet::new();

    node.chain.mine_pending_transactions(&miner_address, &miner_wallet);

    let peers = node.peers.clone();
    drop(node);

    for peer in &peers {
        let _ = std::thread::spawn({
            let peer = peer.clone();
            move || { let _ = reqwest::blocking::get(format!("{}/peers/sync", peer)); }
        }).join();
    }

    HttpResponse::Ok().json(serde_json::json!({"message": "Block mined successfully"}))
}

async fn new_transaction(
    state: web::Data<Mutex<NodeState>>,
    body:  web::Json<TransactionRequest>,
) -> HttpResponse {
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

    // Try Rust native verification first
    let mut valid = verify_transaction(&signed_tx);

    // If that fails try Python liboqs detached signature format
    if !valid {
        if let (Ok(sig_bytes), Ok(pk_bytes)) = (
            hex::decode(&body.signature),
            hex::decode(&body.public_key)
        ) {
            // Try Python JSON format
            valid = verify_detached(
                &tx_data.to_bytes_python(),
                &sig_bytes,
                &pk_bytes,
            );

            // Try Rust colon format
            if !valid {
                valid = verify_detached(
                    &tx_data.to_bytes_rust(),
                    &sig_bytes,
                    &pk_bytes,
                );
            }
        }
    }

    if !valid {
        return HttpResponse::BadRequest().json(
            serde_json::json!({"error": "Invalid signature — transaction rejected"})
        );
    }

    let mut node = state.lock().unwrap();
    node.chain.add_transaction(signed_tx.clone());

    let peers = node.peers.clone();
    drop(node);

    for peer in &peers {
        let client  = reqwest::blocking::Client::new();
        let payload = body.0.clone();
        let peer    = peer.clone();
        std::thread::spawn(move || {
            let _ = client
                .post(format!("{}/transactions/new", peer))
                .json(&payload)
                .send();
        });
    }

    HttpResponse::Ok().json(
        serde_json::json!({"message": "Transaction added to mempool"})
    )
}

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

async fn sync_chain(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    let mut node = state.lock().unwrap();
    let peers    = node.peers.clone();
    let replaced = sync_with_peers(&mut node.chain, &peers);

    if replaced {
        HttpResponse::Ok().json(
            serde_json::json!({"message": "Chain replaced with longer peer chain"})
        )
    } else {
        HttpResponse::Ok().json(
            serde_json::json!({"message": "Our chain is already the longest"})
        )
    }
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
            .route("/peers/sync",        web::get().to(sync_chain))
    })
    .bind(format!("0.0.0.0:{}", port))?
    .run()
    .await
}
