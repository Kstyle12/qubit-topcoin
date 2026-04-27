use pqcrypto_falcon::falcon512;
use pqcrypto_traits::sign::{PublicKey, SecretKey, SignedMessage};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

const IDENTITY_FILE: &str = "qtop_identity.json";

#[derive(Serialize, Deserialize, Clone)]
pub struct NodeIdentity {
    pub public_key: String,
    pub secret_key: String,
    pub node_id:    String, // First 16 bytes of public key hash
}

impl NodeIdentity {
    pub fn new() -> Self {
        let (pk, sk) = falcon512::keypair();

        // Node ID is first 16 hex chars of SHA3 hash of public key
        use sha3::{Digest, Sha3_256};
        let mut hasher = Sha3_256::new();
        hasher.update(pk.as_bytes());
        let hash    = hasher.finalize();
        let node_id = hex::encode(&hash[..8]); // 16 hex chars

        NodeIdentity {
            public_key: hex::encode(pk.as_bytes()),
            secret_key: hex::encode(sk.as_bytes()),
            node_id,
        }
    }

    pub fn load_or_create() -> Self {
        if Path::new(IDENTITY_FILE).exists() {
            match fs::read_to_string(IDENTITY_FILE) {
                Ok(json) => {
                    match serde_json::from_str(&json) {
                        Ok(identity) => {
                            let id: NodeIdentity = identity;
                            println!("  Node ID: {}", id.node_id);
                            return id;
                        }
                        Err(_) => println!("  Invalid identity file, regenerating..."),
                    }
                }
                Err(_) => println!("  Could not read identity file, regenerating..."),
            }
        }

        println!("  Generating new node identity...");
        let identity = NodeIdentity::new();
        let json     = serde_json::to_string_pretty(&identity).unwrap();
        fs::write(IDENTITY_FILE, json).expect("Failed to save identity");
        println!("  Node ID: {}", identity.node_id);
        identity
    }

    pub fn sign(&self, message: &[u8]) -> String {
        let sk_bytes = hex::decode(&self.secret_key).unwrap();
        let sk       = falcon512::SecretKey::from_bytes(&sk_bytes)
            .expect("Invalid node secret key");
        let signed   = falcon512::sign(message, &sk);
        hex::encode(signed.as_bytes())
    }

    pub fn verify(
        public_key_hex: &str,
        message:        &[u8],
        signature_hex:  &str,
    ) -> bool {
        let pk_bytes  = match hex::decode(public_key_hex) {
            Ok(b)  => b,
            Err(_) => return false,
        };
        let pk = match falcon512::PublicKey::from_bytes(&pk_bytes) {
            Ok(k)  => k,
            Err(_) => return false,
        };
        let sig_bytes = match hex::decode(signature_hex) {
            Ok(b)  => b,
            Err(_) => return false,
        };
        let signed_msg = match falcon512::SignedMessage::from_bytes(&sig_bytes) {
            Ok(m)  => m,
            Err(_) => return false,
        };
        match falcon512::open(&signed_msg, &pk) {
            Ok(msg) => msg == message,
            Err(_)  => false,
        }
    }
}
