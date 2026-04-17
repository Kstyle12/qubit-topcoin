import hashlib
import json
import time
from block import Block

class Blockchain:
    def __init__(self):
        self.difficulty          = 4
        self.target_block_time   = 150
        self.adjustment_interval = 10
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
                "fee":       0,
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
                # Miner collects fees from all transactions
                if tx.get("sender") not in ["NETWORK", "GENESIS"]:
                    if tx["recipient"] == address:
                        balance += tx.get("fee", 0)
                    if tx["sender"] == address:
                        balance -= tx.get("fee", 0)
        return balance

    def add_transaction(self, transaction):
        # Sort mempool by fee — highest fee first
        self.mempool.append(transaction)
        self.mempool.sort(
            key=lambda x: x.get("fee", 0),
            reverse=True
        )
        print(f"  Transaction added to mempool "
              f"(fee: {transaction.get('fee', 0)} QTP). "
              f"Pending: {len(self.mempool)}")

    def get_total_fees(self, transactions):
        # Sum all fees in a block — paid to the miner
        total = 0.0
        for tx in transactions:
            if tx.get("sender") not in ["NETWORK", "GENESIS"]:
                total += tx.get("fee", 0)
        return total

    def get_adjusted_difficulty(self):
        if len(self.chain) % self.adjustment_interval != 0:
            return self.difficulty
        if len(self.chain) < self.adjustment_interval:
            return self.difficulty

        last_block    = self.chain[-1]
        first_block   = self.chain[-self.adjustment_interval]
        actual_time   = last_block.timestamp - first_block.timestamp
        expected_time = self.target_block_time * self.adjustment_interval

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
        self.difficulty    = self.get_adjusted_difficulty()
        current_reward     = self.get_current_reward()
        total_fees         = self.get_total_fees(self.mempool)
        total_miner_payout = current_reward + total_fees

        # Reward transaction includes block reward AND all fees
        reward_tx = {
            "sender":    "NETWORK",
            "recipient": miner_address,
            "amount":    total_miner_payout,
            "fee":       0,
            "note":      f"Block {len(self.chain)} reward "
                         f"({current_reward} QTP + "
                         f"{total_fees:.4f} QTP fees)"
        }

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
        print(f"  Miner earned {current_reward} QTP reward "
              f"+ {total_fees:.4f} QTP fees "
              f"= {total_miner_payout:.4f} QTP total")
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
    "amount":    12.5,
    "fee":       0.005
})
qtpchain.add_transaction({
    "sender":    sender_address,
    "recipient": miner_address,
    "amount":    3.0,
    "fee":       0.001
})

qtpchain.mine_pending_transactions(miner_address)

print(f"\nBalance of miner:  {qtpchain.get_balance(miner_address)} QTP")
print(f"Balance of sender: {qtpchain.get_balance(sender_address)} QTP")

valid = qtpchain.is_chain_valid()
print(f"Chain valid: {valid}")

print("")
print("=" * 55)
print("  BLOCKCHAIN COMPLETE")
print("=" * 55)
