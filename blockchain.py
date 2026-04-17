import hashlib
import json
import time
from block import Block

class Blockchain:
    def __init__(self):
        self.difficulty          = 4
        self.target_block_time   = 150  # 2.5 minutes in seconds
        self.adjustment_interval = 10   # adjust every 10 blocks
        self.mempool             = []
        self.block_reward        = 50.0
        self.chain               = [self.create_genesis_block()]

    def create_genesis_block(self):
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
        return self.chain[-1]

    def get_balance(self, address):
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx["recipient"] == address:
                    balance += tx["amount"]
                if tx["sender"] == address:
                    balance -= tx["amount"]
        return balance

    def add_transaction(self, transaction):
        self.mempool.append(transaction)
        print(f"  Transaction added to mempool. "
              f"Pending transactions: {len(self.mempool)}")

    def get_adjusted_difficulty(self):
        # Only adjust every 10 blocks
        if len(self.chain) % self.adjustment_interval != 0:
            return self.difficulty

        # Need at least one full interval to calculate
        if len(self.chain) < self.adjustment_interval:
            return self.difficulty

        # Get timestamps of last adjustment window
        last_block  = self.chain[-1]
        first_block = self.chain[-self.adjustment_interval]

        # How long did the last 10 blocks actually take
        actual_time   = last_block.timestamp - first_block.timestamp

        # How long should they have taken
        expected_time = self.target_block_time * self.adjustment_interval

        # Adjust difficulty up or down
        if actual_time < expected_time / 2:
            new_difficulty = self.difficulty + 1
            print(f"  Difficulty increased to {new_difficulty} "
                  f"(blocks too fast: {actual_time:.0f}s vs "
                  f"{expected_time:.0f}s expected)")
        elif actual_time > expected_time * 2:
            new_difficulty = max(1, self.difficulty - 1)
            print(f"  Difficulty decreased to {new_difficulty} "
                  f"(blocks too slow: {actual_time:.0f}s vs "
                  f"{expected_time:.0f}s expected)")
        else:
            new_difficulty = self.difficulty
            print(f"  Difficulty unchanged at {new_difficulty} "
                  f"(actual: {actual_time:.0f}s, "
                  f"expected: {expected_time:.0f}s)")

        return new_difficulty

    def mine_pending_transactions(self, miner_address):
        # Adjust difficulty before mining
        self.difficulty = self.get_adjusted_difficulty()

        # Create mining reward transaction
        current_reward = self.get_current_reward()
        reward_tx = {
            "sender":    "NETWORK",
            "recipient": miner_address,
            "amount":    current_reward,
            "note":      f"Block {len(self.chain)} mining reward"
        }

        # Bundle reward and mempool transactions
        transactions = [reward_tx] + self.mempool

        new_block = Block(
            index=         len(self.chain),
            transactions=  transactions,
            previous_hash= self.get_latest_block().hash
        )

        print(f"\nMining block {new_block.index} "
              f"at difficulty {self.difficulty}...")
        new_block.mine(self.difficulty)

        self.chain.append(new_block)
        self.mempool = []

        print(f"  Block {new_block.index} added to chain.")
        print(f"  Miner {miner_address[:20]}... "
              f"earned {current_reward} QTP")
        return new_block

    def get_current_reward(self):
        halvings = len(self.chain) // 210000
        reward   = self.block_reward / (2 ** halvings)
        return reward

    def is_chain_valid(self):
        print("\nValidating entire blockchain...")
        for i in range(1, len(self.chain)):
            current  = self.chain[i]
            previous = self.chain[i - 1]

            if not current.is_valid():
                print(f"  INVALID: Block {i} hash is corrupted")
                return False

            if current.previous_hash != previous.hash:
                print(f"  INVALID: Block {i} is disconnected from chain")
                return False

        print(f"  Chain valid — {len(self.chain)} blocks verified")
        return True


# --- TEST ---
print("=" * 55)
print("  QTP BLOCKCHAIN TEST")
print("=" * 55)
print("")

qtpchain = Blockchain()
print("")

miner_address  = "GbtE3vPeomLSRNN2k9DsDfy8YL164JXMw2"
sender_address = "GMVekpeEgiMKED7bQVCVp6nqb8Q597k2FQ"

print("Adding transactions to mempool...")
qtpchain.add_transaction({
    "sender":    miner_address,
    "recipient": sender_address,
    "amount":    12.5
})

qtpchain.mine_pending_transactions(miner_address)

print(f"\nBalance of miner:  {qtpchain.get_balance(miner_address)} QTP")
print(f"Balance of sender: {qtpchain.get_balance(sender_address)} QTP")

valid = qtpchain.is_chain_valid()
print(f"Chain valid: {valid}")

print("\nTampering with block 1...")
qtpchain.chain[1].transactions[0]["amount"] = 999999.0
valid_after = qtpchain.is_chain_valid()
print(f"Chain valid after tampering: {valid_after}")

print("")
print("=" * 55)
print("  BLOCKCHAIN COMPLETE")
print("=" * 55)
