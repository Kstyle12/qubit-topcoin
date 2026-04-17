import hashlib
import json
import time
from block import Block

# --- QTP BLOCKCHAIN ---
# This is the chain itself — the living, growing record of every
# transaction that has ever happened on the QTP network

class Blockchain:
    def __init__(self):
        # Mining difficulty — how many leading zeros a valid hash needs
        # 4 is low for testing, real QTP mainnet will be much higher
        self.difficulty     = 4

        # The mempool holds transactions waiting to be included in a block
        # When a miner mines a block, they pull from here
        self.mempool        = []

        # Mining reward — exactly as specified in the QTP whitepaper
        # 50 QTP per block, halving every 210,000 blocks
        self.block_reward   = 50.0

        # The chain itself — starts with the genesis block
        self.chain          = [self.create_genesis_block()]

    def create_genesis_block(self):
        # The genesis block is the first block — hardcoded into the protocol
        # It has no previous block so previous_hash is all zeros
        # This is block 0 of the QTP blockchain
        print("Creating QTP genesis block...")
        genesis = Block(
            index=         0,
            transactions=  [{
                "sender":    "GENESIS",
                "recipient": "GENESIS",
                "amount":    0,
                "note":      "Qubit TopCoin — For everyone. Forever."
            }],
            previous_hash= "0" * 64
        )
        genesis.mine(self.difficulty)
        return genesis

    def get_latest_block(self):
        # The tip of the chain — the most recently mined block
        return self.chain[-1]

    def get_balance(self, address):
        # Calculate a wallet's balance by scanning every transaction
        # on the entire chain — just like Bitcoin does it
        balance = 0.0

        for block in self.chain:
            for tx in block.transactions:
                # Receiving QTP increases balance
                if tx["recipient"] == address:
                    balance += tx["amount"]
                # Sending QTP decreases balance
                if tx["sender"] == address:
                    balance -= tx["amount"]

        return balance

    def add_transaction(self, transaction):
        # Add a pending transaction to the mempool
        # In a full implementation we would verify the signature here
        # We will add that in the next step
        self.mempool.append(transaction)
        print(f"  Transaction added to mempool. "
              f"Pending transactions: {len(self.mempool)}")

    def mine_pending_transactions(self, miner_address):
        # This is what miners do — they take pending transactions
        # from the mempool, bundle them into a block, and mine it

        # Step 1: Create the mining reward transaction
        # This is how new QTP enters circulation — paid to the miner
        # The halving schedule from the whitepaper is enforced here
        current_reward = self.get_current_reward()
        reward_tx = {
            "sender":    "NETWORK",
            "recipient": miner_address,
            "amount":    current_reward,
            "note":      f"Block {len(self.chain)} mining reward"
        }

        # Step 2: Bundle reward + mempool transactions into a new block
        transactions = [reward_tx] + self.mempool

        new_block = Block(
            index=         len(self.chain),
            transactions=  transactions,
            previous_hash= self.get_latest_block().hash
        )

        # Step 3: Mine the block — this is the proof of work
        print(f"\nMining block {new_block.index}...")
        new_block.mine(self.difficulty)

        # Step 4: Add the mined block to the chain
        self.chain.append(new_block)

        # Step 5: Clear the mempool — those transactions are now confirmed
        self.mempool = []

        print(f"  Block {new_block.index} added to chain.")
        print(f"  Miner {miner_address[:20]}... earned {current_reward} QTP")
        return new_block

    def get_current_reward(self):
        # QTP halving schedule — exactly as in the whitepaper
        # 50 QTP to start, halving every 210,000 blocks
        halvings = len(self.chain) // 210000
        reward   = self.block_reward / (2 ** halvings)
        return reward

    def is_chain_valid(self):
        # Validate the entire chain from block 1 to present
        # This is what every QTP node does when it joins the network
        print("\nValidating entire blockchain...")

        for i in range(1, len(self.chain)):
            current  = self.chain[i]
            previous = self.chain[i - 1]

            # Rule 1: The block's stored hash must match a fresh calculation
            if not current.is_valid():
                print(f"  INVALID: Block {i} hash is corrupted")
                return False

            # Rule 2: This block must point to the previous block's hash
            if current.previous_hash != previous.hash:
                print(f"  INVALID: Block {i} is disconnected from chain")
                return False

        print(f"  Chain valid — {len(self.chain)} blocks verified")
        return True


# --- TEST THE FULL BLOCKCHAIN ---
print("=" * 55)
print("  QTP BLOCKCHAIN TEST")
print("=" * 55)
print("")

# Start the blockchain — this mines the genesis block
qtpchain = Blockchain()
print("")

# Two test wallet addresses
miner_address  = "GbtE3vPeomLSRNN2k9DsDfy8YL164JXMw2"
sender_address = "GMVekpeEgiMKED7bQVCVp6nqb8Q597k2FQ"

# Add some transactions to the mempool
print("Adding transactions to mempool...")
qtpchain.add_transaction({
    "sender":    miner_address,
    "recipient": sender_address,
    "amount":    12.5
})
qtpchain.add_transaction({
    "sender":    sender_address,
    "recipient": miner_address,
    "amount":    3.0
})

# Mine the pending transactions
qtpchain.mine_pending_transactions(miner_address)

# Check balances
print(f"\nBalance of miner:  {qtpchain.get_balance(miner_address)} QTP")
print(f"Balance of sender: {qtpchain.get_balance(sender_address)} QTP")

# Validate the chain
valid = qtpchain.is_chain_valid()
print(f"Chain valid: {valid}")

# Now tamper with the chain and prove it gets caught
print("\nTampering with block 1 transaction...")
qtpchain.chain[1].transactions[0]["amount"] = 999999.0
valid_after_tamper = qtpchain.is_chain_valid()
print(f"Chain valid after tampering: {valid_after_tamper}")

print("")
print("=" * 55)
print("  BLOCKCHAIN COMPLETE")
print("=" * 55)
