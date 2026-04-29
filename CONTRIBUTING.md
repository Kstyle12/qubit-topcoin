# Contributing to Qubit TopCoin

Thank you for your interest in contributing to QTOP. This project is built in public and community contributions are welcome. Please read this document before submitting anything.

## Before You Contribute

Read the [whitepaper](QTOP_Whitepaper.pdf) first. Every technical decision in this codebase exists for a reason rooted in the whitepaper. Understanding the design philosophy will save you time.

## What We Need Most

- **Rust systems programmers** — node performance, networking, storage
- **Post-quantum cryptographers** — FALCON-512 implementation review, security analysis
- **P2P networking specialists** — peer discovery, sync, NAT traversal
- **Security researchers** — audit the cryptographic stack, find bugs
- **Frontend developers** — block explorer improvements, wallet UI

## How to Contribute

### Reporting bugs
Open a GitHub issue. Include your OS, Rust version, and the exact error output. Run this and include the output:
cargo --version
rustc --version
uname -a

### Submitting code
1. Fork the repository
2. Create a branch: `git checkout -b your-feature-name`
3. Make your changes
4. Test thoroughly: `cargo build 2>&1 | grep -E "error|warning"`
5. Commit with a clear message describing what and why
6. Open a pull request against `main`

### Pull request guidelines
- One change per PR — keep it focused
- Explain what you changed and why in the PR description
- All existing functionality must still work after your change
- Zero new compiler warnings — we maintain a clean codebase
- If your change touches cryptography, explain your reasoning in detail

## What We Will Not Merge

- Changes that weaken cryptographic security
- Changes that add inflation or alter the 21,000,000 supply cap
- Changes that give any participant a network advantage
- Mining algorithm changes that favor ASICs or GPUs over CPUs
- Anything that introduces a premine, developer fee, or hidden allocation

## Codebase Overview
qtopcore/src/
├── wallet.rs       — FALCON-512 keypair generation and management
├── transaction.rs  — Transaction signing and verification
├── block.rs        — Block structure and RandomX proof of work
├── blockchain.rs   — Chain management, rewards, halving schedule
├── storage.rs      — Persistent chain storage to disk
├── sync.rs         — Peer chain synchronization
├── identity.rs     — FALCON-512 node identity
├── discovery.rs    — Automatic peer discovery and DNS seeds
├── node.rs         — actix-web REST API
└── bin/
├── miner.rs        — CPU miner with reward tracking
├── send_tx.rs      — Transaction sender
└── wallet_cli.rs   — Encrypted wallet CLI

## Network Status

QTOP is currently on the **Cori Testnet**. Mainnet has not launched. Do not use testnet coins as real currency.

## Security Disclosures

If you find a security vulnerability, do not open a public GitHub issue. Contact the project directly via GitHub private message to @Kstyle12. We take all security reports seriously and will respond promptly.

## Code of Conduct

Be direct. Be honest. Be helpful. This project is built for everyone and contributions from all backgrounds are welcome. The only thing that matters is the quality of the work.

---

*Qubit TopCoin. For everyone. Forever.*
