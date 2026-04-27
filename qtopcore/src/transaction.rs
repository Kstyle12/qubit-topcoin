use pqcrypto_falcon::falcon512;
use pqcrypto_traits::sign::{PublicKey, SecretKey, SignedMessage};
use sha3::{Digest, Sha3_256};
use serde::{Deserialize, Serialize};


#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct TransactionData {
    pub sender:    String,
    pub recipient: String,
    pub amount:    u64,
    pub fee:       u64,
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

    pub fn to_bytes_rust(&self) -> Vec<u8> {
        // Rust native format — colon separated
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

    pub fn to_bytes_python(&self) -> Vec<u8> {
        // Python format — sorted JSON keys
        // Matches json.dumps(transaction, sort_keys=True)
        let json = format!(
            "{{\"amount\": {}, \"fee\": {}, \"recipient\": \"{}\", \"sender\": \"{}\", \"timestamp\": {}}}",
            self.amount,
            self.fee,
            self.recipient,
            self.sender,
            self.timestamp
        );
        json.into_bytes()
    }

    pub fn hash(&self) -> String {
        let mut hasher = Sha3_256::new();
        hasher.update(&self.to_bytes_rust());
        hex::encode(hasher.finalize())
    }
}

pub fn sign_transaction(
    data:       &TransactionData,
    secret_key: &[u8],
    public_key: &[u8],
) -> Result<SignedTransaction, String> {
    let sk = falcon512::SecretKey::from_bytes(secret_key)
        .map_err(|e| format!("Invalid secret key: {:?}", e))?;

    let tx_bytes  = data.to_bytes_rust();
    let signed_msg = falcon512::sign(&tx_bytes, &sk);
    let sig_bytes  = signed_msg.as_bytes().to_vec();

    Ok(SignedTransaction {
        data:       data.clone(),
        hash:       data.hash(),
        signature:  hex::encode(&sig_bytes),
        public_key: hex::encode(public_key),
    })
}

pub fn verify_transaction(signed_tx: &SignedTransaction) -> bool {
    let pk_bytes = match hex::decode(&signed_tx.public_key) {
        Ok(b)  => b,
        Err(_) => return false,
    };

    let pk = match falcon512::PublicKey::from_bytes(&pk_bytes) {
        Ok(k)  => k,
        Err(_) => return false,
    };

    let sig_bytes = match hex::decode(&signed_tx.signature) {
        Ok(b)  => b,
        Err(_) => return false,
    };

    let signed_msg = match falcon512::SignedMessage::from_bytes(&sig_bytes) {
        Ok(m)  => m,
        Err(_) => return false,
    };

    // Try Rust format first
    match falcon512::open(&signed_msg, &pk) {
        Ok(msg) => {
            if msg == signed_tx.data.to_bytes_rust() {
                return true;
            }
            // Try Python format
            if msg == signed_tx.data.to_bytes_python() {
                return true;
            }
            false
        }
        Err(_) => false,
    }
}

pub fn verify_detached(
    message:    &[u8],
    signature:  &[u8],
    public_key: &[u8],
) -> bool {
    // liboqs produces detached signatures
    // We reconstruct a signed message by prepending the signature to the message
    // pqcrypto-falcon signed message format: signature_bytes + message_bytes
    let pk = match falcon512::PublicKey::from_bytes(public_key) {
        Ok(k)  => k,
        Err(_) => return false,
    };

    // Try treating the whole thing as a signed message directly
    let mut signed_msg_bytes = signature.to_vec();
    signed_msg_bytes.extend_from_slice(message);

    if let Ok(signed_msg) = falcon512::SignedMessage::from_bytes(&signed_msg_bytes) {
        if let Ok(recovered) = falcon512::open(&signed_msg, &pk) {
            if recovered == message {
                return true;
            }
        }
    }

    // Try signature alone as signed message
    if let Ok(signed_msg) = falcon512::SignedMessage::from_bytes(signature) {
        if let Ok(recovered) = falcon512::open(&signed_msg, &pk) {
            if recovered == message {
                return true;
            }
        }
    }

    false
}
