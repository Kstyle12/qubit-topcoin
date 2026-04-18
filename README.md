Qubit TopCoin (QTP)

> **Quantum-hardened digital gold. For everyone. Forever.**

Qubit TopCoin is an open source, quantum-resistant cryptocurrency built from the ground up for the post-quantum era. Where Bitcoin and Ethereum rely on elliptic curve cryptography that quantum computers will eventually break, QTP is secured by FALCON-512 — a post-quantum signature scheme standardized by the US National Institute of Standards and Technology (NIST) in 2024.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Network](https://img.shields.io/badge/network-Cori%20Testnet-green.svg)]()
[![Mining](https://img.shields.io/badge/mining-RandomX%20CPU-orange.svg)]()
[![Signatures](https://img.shields.io/badge/signatures-FALCON--512-purple.svg)]()

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Kstyle12/qubit-topcoin.git
cd qubit-topcoin

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install RandomX
brew install cmake
git clone https://github.com/tevador/RandomX.git /tmp/randomx
cd /tmp/randomx && mkdir build && cd build && cmake .. && make && sudo make install
cd ~/qubit-topcoin/qtpcore

# Run a node
cargo run --bin qtpcore -- 5003

# Create a wallet
cargo run --bin qtpwallet -- create

# Check balance
cargo run --bin qtpwallet -- balance

# Open block explorer
open ../explorer.html
```

---

## Why QTP Exists

Every major cryptocurrency today is vulnerable to a sufficiently powerful quantum computer. The threat is not theoretical — it is an engineering timeline. An adversary can harvest encrypted transactions today and decrypt them retroactively once quantum capability arrives. QTP is built to make that impossible, using cryptography designed to remain secure for generations.

---

## Core Properties

| Property | Detail |
|---|---|
| Ticker | QTP |
| Max Supply | 21,000,000 QTP |
| Smallest Unit | 1 cori (0.00000001 QTP) |
| Block Time | 2.5 minutes (target) |
| Block Reward | 50 QTP (halving every 210,000 blocks) |
| Signatures | FALCON-512 (NIST Post-Quantum Standard 2024) |
| Hashing | SHA-3 (Keccak-256) |
| Mining | RandomX (CPU-native, ASIC-resistant) |
| Nodes | Pruned by default (~20-30GB) |
| Premine | None — 100% fair launch |
| Network | Cori Testnet (active) |

---

## What Makes QTP Different

**Quantum-resistant from block zero**
Every other major cryptocurrency is retrofitting quantum resistance onto a vulnerable system. QTP is built with post-quantum cryptography as its foundation — not an afterthought.

**CPU-native mining**
QTP uses RandomX — the same algorithm that powers Monero — which is specifically designed to run best on ordinary CPUs. No ASICs. No GPU farms. A laptop mines QTP on equal terms with a datacenter.

**No premine. No advantage.**
Every QTP in existence is earned through proof-of-work mining beginning at the genesis block. No developer allocation. No foundation reserve. No ICO. The first miner and the last miner play by identical rules.

**Long-term wealth storage**
QTP is designed not just for today's threat landscape but for the next 50 years. FALCON-512 is secure against all currently known quantum algorithms.

**Accessible nodes**
Pruned nodes require only ~20-30GB of storage — stable long-term. Anyone with a standard laptop can run a full validating QTP node forever.

---

## Cryptographic Stack

| Layer | Algorithm | Purpose |
|---|---|---|
| Signatures | FALCON-512 | Wallet ownership proof |
| Hashing | SHA-3 (Keccak-256) | Block and transaction hashing |
| Mining | RandomX | CPU-native proof of work |
| Wallet encryption | AES-256-GCM + PBKDF2 | Private key protection |
| Address encoding | Base58Check | Human-readable addresses |

---

## Architecture
qubit-topcoin/
├── Python Prototype
│   ├── wallet.py
│   ├── transaction.py
│   ├── block.py
│   ├── blockchain.py
│   ├── node.py
│   ├── wallet_manager.py
│   ├── qtpwallet.py
│   └── miner.py
│
├── qtpcore/ (Rust Production Node)
│   └── src/
│       ├── wallet.rs
│       ├── transaction.rs
│       ├── block.rs
│       ├── blockchain.rs
│       ├── storage.rs
│       ├── sync.rs
│       ├── node.rs
│       └── bin/
│           ├── send_tx.rs
│           └── wallet_cli.rs
│
└── explorer.html (Block Explorer)

---

## Cori Testnet

The Cori Testnet is QTP's active test network. Named after QTP's smallest unit of account (1 cori = 0.00000001 QTP), it is the proving ground for the protocol before mainnet launch.

To join — build and run a node following the Quick Start above, connect to a peer, and start mining. Your CPU is a first-class participant.

---

## API Reference
GET  /status              — Node info and network stats
GET  /chain               — Full blockchain data
GET  /mine                — Mine pending transactions
GET  /balance/{address}   — Wallet balance
POST /transactions/new    — Submit a signed transaction
POST /peers/register      — Register a peer node
GET  /peers/sync          — Sync with peer chains

---

## Project Status

| Component | Status |
|---|---|
| FALCON-512 wallet generation | ✅ Working |
| Quantum-resistant transaction signing | ✅ Working |
| RandomX proof of work mining | ✅ Working |
| Blockchain with mining rewards | ✅ Working |
| Automatic difficulty adjustment | ✅ Working |
| Persistent chain storage | ✅ Working |
| P2P network with Nakamoto consensus | ✅ Working |
| AES-256-GCM wallet encryption | ✅ Working |
| Block explorer | ✅ Working |
| Rust production node | ✅ Working |
| Public testnet | 🔧 In progress |
| Security audit | 📋 Planned |
| Mainnet launch | 📋 2027 |

---

## Roadmap

| Phase | Period | Milestone |
|---|---|---|
| Phase 1 | Q1–Q2 2026 | Whitepaper, Python prototype, Rust node |
| Phase 2 | Q3–Q4 2026 | Public Cori Testnet, cloud nodes |
| Phase 3 | Q1–Q2 2027 | Security audit, exchange conversations |
| Phase 4 | Q3 2027 | Mainnet launch |
| Phase 5 | Q4 2027+ | Exchange listings, ecosystem growth |

---

## Contributing

QTP is built in public from day one. Contributions welcome — especially Rust developers, cryptographers, and P2P networking specialists.

---

## Whitepaper

[QTP_Whitepaper.pdf](https://github.com/user-attachments/files/26834896/QTP_Whitepaper.pdf)

---

## License

MIT License — Copyright (c) 2026 Porter Kowalski

---

## Disclaimer

Experimental software on the Cori Testnet. Do not use for real financial transactions. Mainnet has not launched.

---

*Qubit TopCoin. For everyone. Forever.*
