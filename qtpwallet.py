import os
import getpass
import requests
from wallet_manager import generate_wallet, save_wallet, load_wallet
from send_transaction import send_transaction

# --- QTP COMMAND LINE WALLET ---
# A real interactive wallet for the QTP network
# Ties together wallet generation, encryption, and transaction sending

NODE_URL = "http://localhost:5001"

def clear():
    os.system('clear')

def print_header():
    print("=" * 55)
    print("  QUBIT TOPCOIN (QTP) WALLET")
    print("  Quantum-Resistant. For Everyone. Forever.")
    print("=" * 55)
    print("")

def print_menu():
    print("What would you like to do?\n")
    print("  1. Create new wallet")
    print("  2. Open existing wallet")
    print("  3. Check balance")
    print("  4. Send QTP")
    print("  5. Exit")
    print("")

def create_wallet_flow():
    clear()
    print_header()
    print("=== CREATE NEW WALLET ===\n")

    filename = input("Enter a name for your wallet file (e.g. mywallet): ")
    if not filename.endswith(".qtp"):
        filename += ".qtp"

    if os.path.exists(filename):
        print(f"\nA wallet file called {filename} already exists.")
        overwrite = input("Overwrite it? (yes/no): ")
        if overwrite.lower() != "yes":
            return None

    print("\nGenerating FALCON-512 keypair...")
    wallet = generate_wallet()

    print(f"Address generated: {wallet['address']}\n")

    while True:
        password = getpass.getpass("Create a wallet password: ")
        confirm  = getpass.getpass("Confirm password: ")
        if password == confirm:
            break
        print("Passwords do not match. Try again.\n")

    print("\nEncrypting and saving wallet...")
    save_wallet(wallet, filename, password)

    print(f"\n✓ Wallet created successfully")
    print(f"  Address:  {wallet['address']}")
    print(f"  File:     {filename}")
    print(f"\n  Keep your password safe.")
    print(f"  There is no password recovery.\n")

    input("Press Enter to continue...")
    return wallet

def open_wallet_flow():
    clear()
    print_header()
    print("=== OPEN WALLET ===\n")

    # List available wallet files
    wallet_files = [f for f in os.listdir('.') if f.endswith('.qtp')]

    if not wallet_files:
        print("No wallet files found in current directory.")
        print("Create a new wallet first.\n")
        input("Press Enter to continue...")
        return None

    print("Available wallets:")
    for i, f in enumerate(wallet_files, 1):
        print(f"  {i}. {f}")
    print("")

    choice = input("Enter wallet name or number: ")

    # Allow selecting by number
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(wallet_files):
            filename = wallet_files[idx]
        else:
            filename = choice
    except ValueError:
        filename = choice

    if not filename.endswith(".qtp"):
        filename += ".qtp"

    if not os.path.exists(filename):
        print(f"\nWallet file {filename} not found.\n")
        input("Press Enter to continue...")
        return None

    password = getpass.getpass("\nEnter wallet password: ")

    try:
        wallet = load_wallet(filename, password)
        print(f"\n✓ Wallet unlocked")
        print(f"  Address: {wallet['address']}\n")
        input("Press Enter to continue...")
        return wallet
    except ValueError:
        print("\n✗ Wrong password. Wallet could not be opened.\n")
        input("Press Enter to continue...")
        return None

def check_balance_flow(wallet):
    clear()
    print_header()
    print("=== CHECK BALANCE ===\n")

    if not wallet:
        print("No wallet open. Please create or open a wallet first.\n")
        input("Press Enter to continue...")
        return

    print(f"Address: {wallet['address']}")
    print(f"Node:    {NODE_URL}\n")
    print("Checking balance...")

    try:
        response = requests.get(
            f"{NODE_URL}/balance/{wallet['address']}",
            timeout=5
        )
        data    = response.json()
        balance = data.get("balance", 0)
        print(f"\n✓ Balance: {balance} QTP")

        # Convert to cori
        cori = int(balance * 100000000)
        print(f"         {cori} cori\n")

    except Exception:
        print("\n✗ Could not connect to node.")
        print(f"  Make sure node is running at {NODE_URL}\n")

    input("Press Enter to continue...")

def send_qtp_flow(wallet):
    clear()
    print_header()
    print("=== SEND QTP ===\n")

    if not wallet:
        print("No wallet open. Please create or open a wallet first.\n")
        input("Press Enter to continue...")
        return

    print(f"Sending from: {wallet['address']}\n")

    recipient = input("Recipient address: ")
    if not recipient:
        return

    try:
        amount = float(input("Amount to send (QTP): "))
        if amount <= 0:
            print("Amount must be greater than zero.")
            input("Press Enter to continue...")
            return
    except ValueError:
        print("Invalid amount.")
        input("Press Enter to continue...")
        return

    print(f"\nYou are about to send {amount} QTP to:")
    print(f"  {recipient}")
    confirm = input("\nConfirm? (yes/no): ")

    if confirm.lower() != "yes":
        print("Transaction cancelled.\n")
        input("Press Enter to continue...")
        return

    print("\nSigning transaction with FALCON-512...")

    try:
        result = send_transaction(
            sender=            wallet,
            recipient_address= recipient,
            amount=            amount,
            node_url=          NODE_URL
        )
        print(f"\n✓ Transaction submitted to network")
        print(f"  {result}\n")
    except Exception as e:
        print(f"\n✗ Transaction failed: {e}\n")

    input("Press Enter to continue...")

def main():
    clear()
    wallet = None

    while True:
        clear()
        print_header()

        # Show currently open wallet if any
        if wallet:
            print(f"  Open wallet: {wallet['address'][:20]}...\n")
        else:
            print(f"  No wallet open\n")

        print_menu()

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            new_wallet = create_wallet_flow()
            if new_wallet:
                wallet = new_wallet

        elif choice == "2":
            opened = open_wallet_flow()
            if opened:
                wallet = opened

        elif choice == "3":
            check_balance_flow(wallet)

        elif choice == "4":
            send_qtp_flow(wallet)

        elif choice == "5":
            clear()
            print("Goodbye.\n")
            break

        else:
            print("Invalid option. Please choose 1-5.\n")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
