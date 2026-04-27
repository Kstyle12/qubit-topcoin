import hashlib
import json
import time

# --- QTOP BLOCK STRUCTURE ---
# A block is a permanent, tamper-proof container of transactions
# Once added to the chain, nothing inside can ever be changed

class Block:
    def __init__(self, index, transactions, previous_hash):
        # The block's position in the chain (0 = genesis, 1, 2, 3...)
        self.index          = index

        # Every transaction included in this block
        self.transactions   = transactions

        # The hash of the block before this one — this forms the chain
        # If any previous block changes, this breaks, exposing the tampering
        self.previous_hash  = previous_hash

        # When this block was created
        self.timestamp      = time.time()

        # The nonce is the number miners increment trying to find a valid hash
        # We start at 0 — mining will change this
        self.nonce          = 0

        # The block's own fingerprint — calculated from everything above
        self.hash           = self.calculate_hash()

    def calculate_hash(self):
        # Pack everything in the block into one string and hash it
        # sort_keys=True ensures the hash is always consistent
        block_contents = json.dumps({
            "index":         self.index,
            "transactions":  self.transactions,
            "previous_hash": self.previous_hash,
            "timestamp":     self.timestamp,
            "nonce":         self.nonce
        }, sort_keys=True)

        # SHA3-256 — QTOP's chosen hash algorithm
        return hashlib.sha3_256(block_contents.encode()).hexdigest()

    def mine(self, difficulty):
        # Mining means finding a nonce that makes the hash start with
        # a certain number of zeros — e.g. "0000abc123..."
        # The more zeros required, the harder the puzzle
        target = "0" * difficulty

        print(f"  Mining block {self.index}...")
        attempts = 0

        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash   = self.calculate_hash()
            attempts   += 1

        print(f"  Block {self.index} mined in {attempts} attempts!")
        print(f"  Hash: {self.hash}")
        return self.hash

    def is_valid(self):
        # A block is valid if its stored hash matches a fresh calculation
        # If anyone tampered with any field, this will catch it
        return self.hash == self.calculate_hash()

    def to_dict(self):
        # Convert block to a dictionary for display and storage
        return {
            "index":         self.index,
            "timestamp":     self.timestamp,
            "transactions":  self.transactions,
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
            "hash":          self.hash
        }


# --- TEST IT ---
print("=" * 55)
print("  QTOP BLOCK TEST")
print("=" * 55)
print("")

# Create some dummy transactions to put in our test block
test_transactions = [
    {"sender": "GbtE3vPeomLSRNN2k9DsDfy8YL164JXMw2",
     "recipient": "GMVekpeEgiMKED7bQVCVp6nqb8Q597k2FQ",
     "amount": 10.0},
    {"sender": "GMVekpeEgiMKED7bQVCVp6nqb8Q597k2FQ",
     "recipient": "GbtE3vPeomLSRNN2k9DsDfy8YL164JXMw2",
     "amount": 2.5},
]

# The genesis block has no previous block so its previous_hash is all zeros
print("Creating genesis block (block 0)...")
genesis = Block(
    index=         0,
    transactions=  test_transactions,
    previous_hash= "0" * 64
)
print(f"Block created. Hash: {genesis.hash[:40]}...")
print(f"Valid: {genesis.is_valid()}")
print("")

# Mine it at difficulty 4 (hash must start with "0000")
# This is low difficulty for testing — real QTOP will be much higher
print("Mining genesis block at difficulty 4...")
genesis.mine(difficulty=4)
print("")

# Now create block 1 pointing back at the genesis block
print("Creating block 1...")
block_1 = Block(
    index=         1,
    transactions=  [{"sender": "GbtE3vPeomLSRNN2k9DsDfy8YL164JXMw2",
                     "recipient": "GMVekpeEgiMKED7bQVCVp6nqb8Q597k2FQ",
                     "amount": 5.0}],
    previous_hash= genesis.hash
)
block_1.mine(difficulty=4)
print("")

# Test tamper detection
print("Testing tamper detection...")
print(f"Block 1 valid before tampering: {block_1.is_valid()}")
block_1.transactions[0]["amount"] = 999999.0
print(f"Block 1 valid after tampering:  {block_1.is_valid()}")
print("")
print("If the above is False, your block security is working perfectly.")
print("")
print("=" * 55)
