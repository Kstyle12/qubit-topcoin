# Qubit TopCoin (QTOP)

> **Quantum-hardened digital gold. For everyone. Forever.**

Qubit TopCoin is an open source, quantum-resistant cryptocurrency built from
the ground up for the post-quantum era. Where Bitcoin and Ethereum rely on
elliptic curve cryptography that quantum computers will eventually break, QTOP
is secured by FALCON-512 — a post-quantum signature scheme standardized by
the US National Institute of Standards and Technology (NIST) in 2024.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/Kstyle12/qubit-topcoin/blob/main/LICENSE)
[![Network](https://img.shields.io/badge/network-Cori%20Testnet-green.svg)](https://github.com/Kstyle12/qubit-topcoin/blob/main)
[![Mining](https://img.shields.io/badge/mining-RandomX%20CPU-orange.svg)](https://github.com/Kstyle12/qubit-topcoin/blob/main)
[![Signatures](https://img.shields.io/badge/signatures-FALCON--512-purple.svg)](https://github.com/Kstyle12/qubit-topcoin/blob/main)

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Kstyle12/qubit-topcoin.git
cd qubit-topcoin

# One command install (Mac and Linux)
chmod +x install.sh && ./install.sh

# Create a wallet
cd qtopcore
cargo run --bin qtopwallet -- create

# Start a node (rewards paid to your wallet address)
cargo run --bin qtopcore -- 5003 YOUR_QTOP_ADDRESS

# Start mining
cargo run --bin miner -- YOUR_QTOP_ADDRESS

# Open the block explorer
open ../explorer.html
```

---

## Why QTOP Exists

Every major cryptocurrency today is vulnerable to a sufficiently powerful
quantum computer. The threat is not theoretical — it is an engineering
timeline. An adversary can harvest encrypted transactions today and decrypt
them retroactively once quantum capability arrives — a strategy known as
"harvest now, decrypt later."

QTOP is built to make that impossible, using cryptography designed to remain
secure for generations.

---

## Core Properties

| Property | Detail |
| --- | --- |
| Ticker | QTOP |
| Max Supply | 21,000,000 QTOP |
| Smallest Unit | 1 cori (0.00000001 QTOP) |
| Block Time | 2.5 minutes (target) |
| Block Reward | 50 QTOP (halving every 210,000 blocks) |
| Signatures | FALCON-512 (NIST Post-Quantum Standard 2024) |
| Hashing | SHA-3 (Keccak-256) |
| Mining | RandomX (CPU-native, ASIC-resistant) |
| Node Storage | ~20-30GB pruned (stable long-term) |
| Premine | None — 100% fair launch |
| Network | Cori Testnet (active) |

---

## What Makes QTOP Different

**Quantum-resistant from block zero**
Every other major cryptocurrency is retrofitting quantum resistance onto a
vulnerable system. QTOP is built with post-quantum cryptography as its
foundation — not an afterthought.

**CPU-native mining with RandomX**
QTOP uses RandomX — the same algorithm that powers Monero — specifically
designed to run best on ordinary CPUs. No ASICs. No GPU farms. A laptop
mines QTOP on equal terms with a datacenter. This is how decentralization
stays real.

**FALCON-512 node identity**
Every QTOP node has a persistent FALCON-512 keypair as its network identity.
All node communications are authenticated with post-quantum signatures —
not just transactions.

**No premine. No advantage.**
Every QTOP in existence is earned through proof-of-work mining beginning at
the genesis block. No developer allocation. No foundation reserve. No ICO.
The first miner and the last miner play by identical rules.

**Long-term wealth storage**
QTOP is designed not just for today's threat landscape but for the next 50
years. FALCON-512 is secure against all currently known quantum algorithms.
A fixed supply of 21,000,000 QTOP combined with quantum-resistant security
makes QTOP a credible generational store of value.

---

## Cryptographic Stack

| Layer | Algorithm | Purpose |
| --- | --- | --- |
| Transaction signatures | FALCON-512 | Wallet ownership proof |
| Node identity | FALCON-512 | P2P authentication |
| Block hashing | SHA-3 (Keccak-256) | Chain integrity |
| Proof of work | RandomX | CPU-native mining |
| Wallet encryption | AES-256-GCM + PBKDF2 | Private key protection |
| Address encoding | Base58Check | Human-readable addresses |

---

## Running a Node

```bash
cd qtopcore

# Basic node (rewards go to internal wallet)
cargo run --bin qtopcore -- 5003

# Node with your wallet address (recommended)
cargo run --bin qtopcore -- 5003 YOUR_QTOP_ADDRESS

# Check node status
curl http://localhost:5003/status

# Check your balance
curl http://localhost:5003/balance/YOUR_QTOP_ADDRESS
```

---

## Mining

```bash
cd qtopcore

# Start the CPU miner
cargo run --bin miner -- YOUR_QTOP_ADDRESS

# Mine to a different node
cargo run --bin miner -- YOUR_QTOP_ADDRESS http://node-address:5003
```

The miner automatically:

* Connects to your node
* Registers your wallet address for rewards
* Polls for pending transactions every 5 seconds
* Mines blocks using RandomX proof of work
* Tracks earnings and displays wallet balance

---

## Wallet

```bash
cd qtopcore

# Create new encrypted wallet
cargo run --bin qtopwallet -- create

# Check balance
cargo run --bin qtopwallet -- balance

# Send QTOP
cargo run --bin qtopwallet -- send

# Show address
cargo run --bin qtopwallet -- address
```

Wallets are encrypted with AES-256-GCM and PBKDF2 key derivation.
Your private key is never stored in plain text.

---

## API Reference
GET  /status                  Node info and network stats
GET  /chain                   Full blockchain data
GET  /mine                    Mine pending transactions
GET  /identity                Node FALCON-512 public key
GET  /balance/{address}       Wallet balance in cori and QTOP
POST /transactions/new        Submit a signed transaction
POST /peers/register          Register a peer node
GET  /peers/sync              Sync with peer chains

---

## Linux Server Deployment

```bash
# Install everything
curl -sSL https://raw.githubusercontent.com/Kstyle12/qubit-topcoin/main/install.sh | bash

# Set up as a permanent background service
curl -sSL https://raw.githubusercontent.com/Kstyle12/qubit-topcoin/main/setup_service.sh | bash

# Check service status
sudo systemctl status qtop-node

# View live logs
sudo journalctl -u qtop-node -f
```

---

## Block Explorer

Open `explorer.html` in your browser while a node is running on port 5003.

Features:

* Real-time block and transaction data
* Node identity and FALCON-512 public key display
* Address balance lookup
* RandomX mining algorithm confirmation
* Auto-refreshes every 10 seconds

---

## Architecture
qubit-topcoin/
├── Python Prototype          # Proof of concept
│   ├── wallet.py
│   ├── transaction.py
│   ├── block.py
│   ├── blockchain.py
│   ├── node.py
│   ├── wallet_manager.py
│   ├── qtpwallet.py
│   └── miner.py
│
├── qtopcore/                 # Production Rust node
│   └── src/
│       ├── wallet.rs         # FALCON-512 keypair generation
│       ├── transaction.rs    # Signing and verification
│       ├── block.rs          # RandomX proof of work
│       ├── blockchain.rs     # Chain with halving schedule
│       ├── storage.rs        # Persistent chain to disk
│       ├── sync.rs           # Peer chain synchronization
│       ├── identity.rs       # FALCON-512 node identity
│       ├── discovery.rs      # Automatic peer discovery
│       ├── node.rs           # actix-web REST API
│       └── bin/
│           ├── miner.rs      # CPU miner with reward tracking
│           ├── send_tx.rs    # Transaction sender
│           └── wallet_cli.rs # Encrypted wallet CLI
│
├── explorer.html             # Block explorer
├── install.sh                # One-command installer
├── setup_service.sh          # Linux systemd service setup
└── QTOP_Whitepaper.pdf       # Technical whitepaper

---

## Project Status

| Component | Status |
| --- | --- |
| FALCON-512 wallet generation | ✅ Complete |
| Quantum-resistant transaction signing | ✅ Complete |
| RandomX CPU mining | ✅ Complete |
| Mining rewards to wallet | ✅ Complete |
| Automatic difficulty adjustment | ✅ Complete |
| Persistent chain storage | ✅ Complete |
| P2P network with Nakamoto consensus | ✅ Complete |
| FALCON-512 node identity | ✅ Complete |
| Automatic peer discovery | ✅ Complete |
| AES-256-GCM wallet encryption | ✅ Complete |
| Block explorer | ✅ Complete |
| One-command installer | ✅ Complete |
| Linux systemd service | ✅ Complete |
| Public testnet | 🔧 In progress |
| Security audit | 📋 Planned |
| Mainnet launch | 📋 2027 |

---

## Cori Testnet

The Cori Testnet is QTOP's active test network. Named after QTOP's smallest
unit of account (1 cori = 0.00000001 QTOP).

To join:

1. Run the installer
2. Create a wallet
3. Start a node with your wallet address
4. Start mining

Your CPU is a first-class participant.

---

## Contributing

QTOP is built in public from day one. Contributions welcome — especially:

* Rust systems programmers
* Post-quantum cryptographers
* P2P networking specialists
* Security researchers

Read the whitepaper before contributing.

---

## Whitepaper

[QTOP_Whitepaper.pdf](https://github.com/user-attachments/files/26862089/QTP_Whitepaper.pdf)

---

## License

MIT License — Copyright (c) 2026 Porter Kowalski

---

## Disclaimer

Experimental software on the Cori Testnet. Do not use for real financial
transactions. Mainnet has not launched.

---

*Qubit TopCoin. For everyone. Forever.*