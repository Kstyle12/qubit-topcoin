use actix_web::{web, App, HttpServer, HttpResponse};
use actix_cors::Cors;
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use crate::blockchain::Blockchain;
use crate::wallet::Wallet;
use crate::transaction::{TransactionData, SignedTransaction, verify_transaction, verify_detached};
use crate::sync::sync_with_peers;
use crate::identity::NodeIdentity;

pub struct NodeState {
    pub chain:         Blockchain,
    pub peers:         Vec<String>,
    pub miner_address: String,
    pub identity:      NodeIdentity,
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

#[derive(Serialize, Deserialize, Clone)]
pub struct PeerRequest {
    pub peer:       String,
    pub node_id:    Option<String>,
    pub public_key: Option<String>,
}

#[derive(Serialize)]
pub struct StatusResponse {
    pub status:      String,
    pub node_id:     String,
    pub public_key:  String,
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
    pub qtop:    f64,
}

async fn get_status(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    let node   = state.lock().unwrap();
    let latest = node.chain.latest_block();
    HttpResponse::Ok().json(StatusResponse {
        status:      "running".to_string(),
        node_id:     node.identity.node_id.clone(),
        public_key:  node.identity.public_key.clone(),
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

    // Mine even if mempool is empty — miner still gets block reward

    let miner_address = node.miner_address.clone();
    let temp_wallet   = Wallet::new();

    node.chain.mine_pending_transactions(&miner_address, &temp_wallet);

    // Sign the new block hash with node identity
    let latest    = node.chain.latest_block();
    let signature = node.identity.sign(latest.hash.as_bytes());

    let peers = node.peers.clone();
    drop(node);

    for peer in &peers {
        let _ = std::thread::spawn({
            let peer = peer.clone();
            move || { let _ = reqwest::blocking::get(format!("{}/peers/sync", peer)); }
        }).join();
    }

    HttpResponse::Ok().json(serde_json::json!({
        "message":   "Block mined successfully",
        "signature": signature,
    }))
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

    let mut valid = verify_transaction(&signed_tx);

    if !valid {
        if let (Ok(sig_bytes), Ok(pk_bytes)) = (
            hex::decode(&body.signature),
            hex::decode(&body.public_key)
        ) {
            valid = verify_detached(
                &tx_data.to_bytes_python(),
                &sig_bytes,
                &pk_bytes,
            );
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
        qtop: balance as f64 / 100_000_000.0,
    })
}

async fn register_peer(
    state: web::Data<Mutex<NodeState>>,
    body:  web::Json<PeerRequest>,
) -> HttpResponse {
    let mut node = state.lock().unwrap();
    if !node.peers.contains(&body.peer) {
        node.peers.push(body.peer.clone());
        println!(
            "  Peer registered: {} (ID: {})",
            body.peer,
            body.node_id.as_deref().unwrap_or("unknown")
        );
    }
    HttpResponse::Ok().json(serde_json::json!({
        "message":    format!("Peer {} registered", body.peer),
        "peers":      node.peers.clone(),
        "our_node_id": node.identity.node_id.clone(),
    }))
}




async fn set_miner_address(
    state:   web::Data<Mutex<NodeState>>,
    address: web::Path<String>,
) -> HttpResponse {
    let mut node = state.lock().unwrap();
    node.miner_address = address.to_string();
    println!("  Miner address set to: {}", address);
    HttpResponse::Ok().json(serde_json::json!({
        "message": format!("Miner address set to {}", address),
        "address": address.to_string(),
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

// GET /identity — expose this node's public identity
async fn get_identity(state: web::Data<Mutex<NodeState>>) -> HttpResponse {
    let node = state.lock().unwrap();
    HttpResponse::Ok().json(serde_json::json!({
        "node_id":    node.identity.node_id.clone(),
        "public_key": node.identity.public_key.clone(),
    }))
}

pub async fn start_node(port: u16, miner_addr: Option<String>) -> std::io::Result<()> {
    println!("=========================================");
    println!("  QTOP NODE STARTING ON PORT {}", port);
    println!("=========================================");
    println!("Loading node identity...");

    let identity = NodeIdentity::load_or_create();

    println!("=========================================");
    println!("  Endpoints:");
    println!("  GET  /status");
    println!("  GET  /chain");
    println!("  GET  /mine");
    println!("  GET  /identity");
    println!("  GET  /balance/{{address}}");
    println!("  POST /transactions/new");
    println!("  POST /peers/register");
    println!("  GET  /peers/sync");
    println!("=========================================");

    // Discover peers automatically on startup
    println!("Discovering peers...");
    let discovered = crate::discovery::discover_peers();
    let reachable  = crate::discovery::filter_reachable(discovered);

    if reachable.is_empty() {
        println!("  No reachable peers found - starting as bootstrap node");
    } else {
        println!("  Connected to {} peer(s)", reachable.len());
    }

    let default_miner = miner_addr.unwrap_or_else(|| {
        Wallet::new().address
    });
    println!("  Mining rewards -> {}", &default_miner[..20]);

    let state = web::Data::new(Mutex::new(NodeState {
        chain:         Blockchain::new(),
        peers:         reachable,
        miner_address: default_miner,
        identity,
    }));

    HttpServer::new(move || {
        App::new()
            .wrap(Cors::permissive())
            .app_data(state.clone())
            .route("/status",            web::get().to(get_status))
            .route("/chain",             web::get().to(get_chain))
            .route("/mine",              web::get().to(mine))
            .route("/set_miner/{address}", web::post().to(set_miner_address))
            .route("/identity",          web::get().to(get_identity))
            .route("/balance/{address}", web::get().to(get_balance))
            .route("/transactions/new",  web::post().to(new_transaction))
            .route("/peers/register",    web::post().to(register_peer))
            .route("/peers/sync",        web::get().to(sync_chain))
    })
    .bind(format!("0.0.0.0:{}", port))?
    .run()
    .await
}
