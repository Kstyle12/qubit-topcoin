use pqcrypto_falcon::falcon512;
use pqcrypto_traits::sign::{PublicKey, SecretKey, SignedMessage};
use sha3::{Digest, Sha3_256};
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct TransactionData {
    pub sender:    String,
    pub recipient: String,
    pub amount:    u64,      // Amount in cori (1 QTP = 100,000,000 cori)
    pub fee:       u64,      // Fee in cori
    pub timestamp: u64,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SignedTransaction {
    pub data:       TransactionData,
    pub hash:       String,
    pub signature:  String,
    pub public_key: String,
}

impl TransactionData {
    pub fn new(
        sender:    String,
        recipient: String,
        amount:    u64,
        fee:       u64,
    ) -> Self {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        TransactionData { sender, recipient, amount, fee, timestamp }
    }

    pub fn to_bytes(&self) -> Vec<u8> {
        // Serialize deterministically for signing
        let s = format!(
            "{}:{}:{}:{}:{}",
            self.sender,
            self.recipient,
            self.amount,
            self.fee,
            self.timestamp
        );
        s.into_bytes()
    }

    pub fn hash(&self) -> String {
        let mut hasher = Sha3_256::new();
        hasher.update(&self.to_bytes());
        hex::encode(hasher.finalize())
    }
}

pub fn sign_transaction(
    data:       &TransactionData,
    secret_key: &[u8],
    public_key: &[u8],
) -> Result<SignedTransaction, String> {
    // Reconstruct secret key from bytes
    let sk = falcon512::SecretKey::from_bytes(secret_key)
        .map_err(|e| format!("Invalid secret key: {:?}", e))?;

    // Sign the transaction bytes
    let tx_bytes  = data.to_bytes();
    let signed_msg = falcon512::sign(&tx_bytes, &sk);

    // Extract just the signature bytes
    let sig_bytes = signed_msg.as_bytes().to_vec();

    Ok(SignedTransaction {
        data:       data.clone(),
        hash:       data.hash(),
        signature:  hex::encode(&sig_bytes),
        public_key: hex::encode(public_key),
    })
}

pub fn verify_transaction(signed_tx: &SignedTransaction) -> bool {
    // Reconstruct public key
    let pk_bytes = match hex::decode(&signed_tx.public_key) {
        Ok(b)  => b,
        Err(_) => return false,
    };

    let pk = match falcon512::PublicKey::from_bytes(&pk_bytes) {
        Ok(k)  => k,
        Err(_) => return false,
    };

    // Reconstruct signed message
    let sig_bytes = match hex::decode(&signed_tx.signature) {
        Ok(b)  => b,
        Err(_) => return false,
    };

    let signed_msg = match falcon512::SignedMessage::from_bytes(&sig_bytes) {
        Ok(m)  => m,
        Err(_) => return false,
    };

    // Verify — returns the original message if valid
    match falcon512::open(&signed_msg, &pk) {
        Ok(msg) => msg == signed_tx.data.to_bytes(),
        Err(_)  => false,
    }
}
