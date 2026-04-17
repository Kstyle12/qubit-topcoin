import sys
import time
import requests
import threading

# --- QTP MINER ---
# A simple command line miner for the QTP network
# Run this to start mining and earning QTP rewards

NODE_URL     = "http://localhost:5001"
POLL_INTERVAL = 5  # seconds between mining attempts

def print_header():
    print("=" * 55)
    print("  QUBIT TOPCOIN (QTP) MINER")
    print("  Quantum-Resistant. For Everyone. Forever.")
    print("=" * 55)
    print("")

def get_node_status():
    try:
        response = requests.get(f"{NODE_URL}/status", timeout=5)
        return response.json()
    except Exception:
        return None

def mine_block():
    try:
        response = requests.get(f"{NODE_URL}/mine", timeout=300)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def check_balance(address):
    try:
        response = requests.get(
            f"{NODE_URL}/balance/{address}",
            timeout=5
        )
        return response.json().get("balance", 0)
    except Exception:
        return None

def mining_loop(miner_address):
    print(f"Mining to address: {miner_address}")
    print(f"Connected to node: {NODE_URL}")
    print(f"Press Ctrl+C to stop mining\n")
    print("-" * 55)

    blocks_mined  = 0
    total_earned  = 0.0
    start_time    = time.time()

    while True:
        try:
            # Check node status
            status = get_node_status()
            if not status:
                print(f"[{timestamp()}] Node unreachable. "
                      f"Retrying in {POLL_INTERVAL}s...")
                time.sleep(POLL_INTERVAL)
                continue

            pending = status.get("pending_txs", 0)
            blocks  = status.get("blocks", 0)

            if pending == 0:
                print(f"[{timestamp()}] No pending transactions. "
                      f"Waiting {POLL_INTERVAL}s... "
                      f"(chain height: {blocks})")
                time.sleep(POLL_INTERVAL)
                continue

            # Mine pending transactions
            print(f"[{timestamp()}] {pending} pending transaction(s) found. "
                  f"Mining...")

            result = mine_block()

            if "error" in result:
                print(f"[{timestamp()}] Mining error: {result['error']}")
                time.sleep(POLL_INTERVAL)
                continue

            if "message" in result and "mined" in result["message"]:
                blocks_mined += 1
                reward        = result.get("reward", 50.0)
                total_earned += reward
                elapsed       = time.time() - start_time

                print(f"[{timestamp()}] ✓ Block mined!")
                print(f"  Hash:         {result.get('hash', '')[:40]}...")
                print(f"  Reward:       {reward} QTP")
                print(f"  Total earned: {total_earned} QTP "
                      f"({blocks_mined} blocks)")
                print(f"  Mining time:  {elapsed:.0f}s total")

                # Check wallet balance
                balance = check_balance(miner_address)
                if balance is not None:
                    print(f"  Wallet balance: {balance} QTP")
                print("-" * 55)

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print(f"\n\n{'=' * 55}")
            print(f"  MINING STOPPED")
            print(f"{'=' * 55}")
            print(f"  Blocks mined:  {blocks_mined}")
            print(f"  Total earned:  {total_earned} QTP")
            print(f"  Time elapsed:  {time.time() - start_time:.0f}s")
            print(f"{'=' * 55}\n")
            sys.exit(0)

def timestamp():
    return time.strftime("%H:%M:%S")

def main():
    print_header()

    # Get miner address
    if len(sys.argv) > 1:
        miner_address = sys.argv[1]
    else:
        print("Usage: python3 miner.py <your_qtp_address>")
        print("Example: python3 miner.py GbtE3vPeomLSRNN2k9DsDfy8YL164JXMw2")
        print("")
        miner_address = input("Enter your QTP wallet address: ").strip()
        if not miner_address:
            print("No address provided. Exiting.")
            sys.exit(1)

    print("")

    # Check node is reachable before starting
    print("Connecting to node...")
    status = get_node_status()
    if not status:
        print(f"Cannot reach node at {NODE_URL}")
        print("Make sure your node is running with: python3 node.py 5001")
        sys.exit(1)

    print(f"Connected. Chain height: {status.get('blocks', 0)} blocks")
    print("")

    # Start mining
    mining_loop(miner_address)

if __name__ == "__main__":
    main()
