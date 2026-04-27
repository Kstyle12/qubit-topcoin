use pqcrypto_falcon::falcon512;
use pqcrypto_traits::sign::{PublicKey, SecretKey};
use sha3::{Digest, Sha3_256};

pub struct Wallet {
    pub address:    String,
    pub public_key: Vec<u8>,
    pub secret_key: Vec<u8>,
}

impl Wallet {
    pub fn new() -> Self {
        let (public_key, secret_key) = falcon512::keypair();

        let mut hasher = Sha3_256::new();
        hasher.update(public_key.as_bytes());
        let hash = hasher.finalize();

        let address_bytes = &hash[hash.len() - 20..];
        let mut versioned  = vec![0x26u8];
        versioned.extend_from_slice(address_bytes);

        let mut h2 = Sha3_256::new();
        h2.update(&versioned);
        let first_hash = h2.finalize();

        let mut h3 = Sha3_256::new();
        h3.update(&first_hash);
        let second_hash = h3.finalize();

        let mut full_address = versioned.clone();
        full_address.extend_from_slice(&second_hash[..4]);
        let address = bs58::encode(&full_address).into_string();

        Wallet {
            address,
            public_key: public_key.as_bytes().to_vec(),
            secret_key: secret_key.as_bytes().to_vec(),
        }
    }

    pub fn public_key_hex(&self) -> String {
        hex::encode(&self.public_key)
    }

    pub fn secret_key_hex(&self) -> String {
        hex::encode(&self.secret_key)
    }
}
