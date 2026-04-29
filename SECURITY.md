# Security Policy

## Overview

Qubit TopCoin takes security seriously. This document outlines our security policy, how to report vulnerabilities, and what we consider in scope. QTOP is currently on the Cori Testnet — mainnet has not launched. All security findings, however small, are taken seriously and will be addressed transparently.

## Supported Versions

| Version | Network | Status |
| --- | --- | --- |
| Current | Cori Testnet | Active — reports welcome |
| Mainnet | Not yet launched | — |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

If you discover a security vulnerability, please report it privately:

- GitHub: Send a private message to [@Kstyle12](https://github.com/Kstyle12)
- Include as much detail as possible — steps to reproduce, impact, and any suggested fixes

We will respond within 72 hours. We take all reports seriously regardless of severity.

## What Happens After You Report

1. We acknowledge receipt within 72 hours
2. We investigate and confirm the vulnerability
3. We develop and test a fix
4. We release the fix and disclose the vulnerability publicly with credit to the reporter
5. We never silently patch — all security fixes are disclosed transparently

## Scope

### In scope
- FALCON-512 signature implementation vulnerabilities
- RandomX proof-of-work weaknesses or bypass attacks
- Double-spend vulnerabilities
- Consensus bugs that could allow chain manipulation
- Wallet encryption weaknesses (AES-256-GCM / PBKDF2)
- Node identity and P2P authentication vulnerabilities
- Denial of service attacks against node software
- Supply cap bypass — any mechanism that could mint coins beyond 21,000,000 QTOP

### Out of scope
- Bugs in third-party dependencies (report these upstream)
- Issues requiring physical access to a device
- Social engineering attacks
- Theoretical attacks with no practical exploit path

## Cryptographic Stack

QTOP's security model is layered. Each layer is independently selected and a compromise of one layer does not collapse the system:

| Layer | Algorithm | Known quantum resistance |
| --- | --- | --- |
| Transaction signatures | FALCON-512 | Yes — NIST PQC standard 2024 |
| Node identity | FALCON-512 | Yes — NIST PQC standard 2024 |
| Block hashing | SHA-3 / Keccak-256 | Yes — strong security margins |
| Proof of work | RandomX | Yes — memory-hard, ASIC resistant |
| Wallet encryption | AES-256-GCM + PBKDF2 | Yes — symmetric, Grover-resistant at 256-bit |

## Testnet Notice

QTOP is currently in testnet phase. Testnet coins have no monetary value. Security research on the Cori Testnet is welcome and encouraged. Please do not attempt to disrupt the testnet in ways that would prevent other participants from using it.

## Responsible Disclosure

We follow responsible disclosure principles. We ask that researchers:

- Give us reasonable time to fix issues before public disclosure
- Avoid accessing or modifying other users' data
- Avoid disrupting the testnet network for other participants
- Act in good faith

In return we commit to:

- Responding promptly
- Keeping you informed throughout the process
- Publicly crediting researchers who report valid vulnerabilities
- Never pursuing legal action against good-faith security researchers

## Bug Bounty

There is no formal bug bounty program at this time. We are a community project in testnet phase. Critical vulnerability reporters will be publicly credited and recognized in the project.

---

*Qubit TopCoin. For everyone. Forever.*
