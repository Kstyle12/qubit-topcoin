# Qubit TopCoin (QTP)

> **Quantum-hardened digital gold. For everyone. Forever.**

Qubit TopCoin is an open source, quantum-resistant cryptocurrency built from 
the ground up for the post-quantum era. Where Bitcoin and Ethereum rely on 
elliptic curve cryptography that quantum computers will eventually break, QTP 
is secured by FALCON-512 — a post-quantum signature scheme standardized by 
the US National Institute of Standards and Technology (NIST) in 2024.

QTP is designed to be one of the most cryptographically secure stores of value 
ever created — and accessible to everyone equally.

---

## Why QTP Exists

Every major cryptocurrency today is vulnerable to a sufficiently powerful 
quantum computer. The threat is not theoretical — it is an engineering timeline. 
An adversary can harvest encrypted transactions today and decrypt them 
retroactively once quantum capability arrives. QTP is built to make that 
impossible, using cryptography designed to remain secure for generations.

---

## Core Properties

| Property | Detail |
|---|---|
| Ticker | QTP |
| Max Supply | 21,000,000 QTP |
| Smallest Unit | 1 cori (0.00000001 QTP) |
| Block Time | 2.5 minutes |
| Block Reward | 50 QTP (halving every 210,000 blocks) |
| Signatures | FALCON-512 (NIST Post-Quantum Standard) |
| Hashing | SHA-3 (Keccak-256) |
| Mining | RandomX (CPU-native, ASIC-resistant) |
| Nodes | Pruned by default (~20-30GB) |
| Premine | None |

---

## What Makes QTP Different

**Quantum-resistant from block zero**
Every other major cryptocurrency is retrofitting quantum resistance onto an 
existing vulnerable system. QTP is built with post-quantum cryptography as 
its foundation — not an afterthought.

**CPU-native mining**
QTP uses RandomX — the same algorithm that powers Monero — which is 
specifically designed to run best on ordinary CPUs. No ASICs. No GPU farms. 
A laptop mines QTP on equal terms with a datacenter. This is how 
decentralization stays real.

**No premine. No advantage.**
Every QTP in existence is earned through proof-of-work mining beginning at 
the genesis block. No developer allocation. No foundation reserve. No ICO. 
The first miner and the last miner play by identical rules.

**Long-term wealth storage**
QTP is designed not just for today's threat landscape but for the next 50 
years. FALCON-512 is secure against all currently known quantum algorithms. 
A fixed supply of 21,000,000 QTP combined with quantum-resistant security 
makes QTP a credible generational store of value.

**Accessible nodes**
Pruned nodes require only ~20-30GB of storage — stable long-term. Anyone 
with a standard laptop can run a full validating QTP node forever.

---

## Cryptographic Stack

| Layer | Algorithm | Purpose |
|---|---|---|
| Signatures | FALCON-512 | Wallet ownership proof |
| Hashing | SHA-3 (Keccak-256) | Block and transaction hashing |
| Mining | RandomX | Proof of work |
| Address encoding | Base58Check | Human-readable addresses |

---

## Project Status

This repository contains a working Python prototype demonstrating QTP's 
core concepts. It is not production software.

| Component | Status |
|---|---|
| FALCON-512 wallet generation | ✅ Working |
| Quantum-resistant transaction signing | ✅ Working |
| Proof of work block mining | ✅ Working |
| Blockchain with mining rewards | ✅ Working |
| P2P node networking | 🔧 In progress |
| Full node software (Rust) | 📋 Planned |
| Public testnet | 📋 2026 |
| Mainnet launch | 📋 2027 |

---

## Whitepaper

The full QTP whitepaper covering technical design, tokenomics, consensus 
mechanism, and roadmap is available in this repository.

[Read the QTP Whitepaper](./QTP_Whitepaper.pdf)

---

## Running the Prototype

**Requirements:** Mac or Linux, Python 3.9+, liboqs

```bash
