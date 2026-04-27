#!/bin/bash

# =========================================
#   QTOP — Qubit TopCoin Node Installer
#   Cori Testnet
#   github.com/Kstyle12/qubit-topcoin
# =========================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  QUBIT TOPCOIN (QTOP) NODE INSTALLER${NC}"
echo -e "${BLUE}  Cori Testnet${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
fi

echo -e "${GREEN}Detected OS: $OS${NC}"
echo ""

# ---- STEP 1: Install dependencies ----
echo -e "${BLUE}[1/5] Installing dependencies...${NC}"

if [ "$OS" == "mac" ]; then
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install cmake git
elif [ "$OS" == "linux" ]; then
    sudo apt-get update -q
    sudo apt-get install -y cmake git build-essential curl pkg-config libssl-dev
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# ---- STEP 2: Install Rust ----
echo -e "${BLUE}[2/5] Installing Rust...${NC}"

if ! command -v rustc &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
else
    echo "Rust already installed: $(rustc --version)"
fi

source "$HOME/.cargo/env"
echo -e "${GREEN}✓ Rust ready: $(rustc --version)${NC}"
echo ""

# ---- STEP 3: Install RandomX ----
echo -e "${BLUE}[3/5] Installing RandomX...${NC}"

if [ ! -f /usr/local/lib/librandomx.a ] && [ ! -f /usr/lib/librandomx.a ]; then
    echo "Building RandomX from source..."
    git clone --depth 1 https://github.com/tevador/RandomX.git /tmp/randomx-build
    cd /tmp/randomx-build
    mkdir -p build && cd build
    cmake ..
    make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
    sudo make install
    cd ~
    rm -rf /tmp/randomx-build
    echo -e "${GREEN}✓ RandomX installed${NC}"
else
    echo -e "${GREEN}✓ RandomX already installed${NC}"
fi
echo ""

# ---- STEP 4: Clone and build QTOP ----
echo -e "${BLUE}[4/5] Building QTOP node...${NC}"

if [ ! -d "$HOME/qubit-topcoin" ]; then
    git clone https://github.com/Kstyle12/qubit-topcoin.git "$HOME/qubit-topcoin"
else
    echo "Repository already exists, pulling latest..."
    cd "$HOME/qubit-topcoin"
    git pull
fi

cd "$HOME/qubit-topcoin/qtopcore"
cargo build --release --bin qtopcore
cargo build --release --bin qtopwallet

echo -e "${GREEN}✓ QTOP node built successfully${NC}"
echo ""

# ---- STEP 5: Create startup script ----
echo -e "${BLUE}[5/5] Creating startup script...${NC}"

cat > "$HOME/qubit-topcoin/start_node.sh" << 'STARTSCRIPT'
#!/bin/bash
cd "$HOME/qubit-topcoin/qtopcore"
source "$HOME/.cargo/env"

PORT=${1:-5003}
echo "Starting QTOP node on port $PORT..."
./target/release/qtopcore $PORT
STARTSCRIPT

chmod +x "$HOME/qubit-topcoin/start_node.sh"

# Create wallet shortcut
cat > "$HOME/qubit-topcoin/wallet.sh" << 'WALLETSCRIPT'
#!/bin/bash
cd "$HOME/qubit-topcoin/qtopcore"
source "$HOME/.cargo/env"
./target/release/qtopwallet "$@"
WALLETSCRIPT

chmod +x "$HOME/qubit-topcoin/wallet.sh"

echo -e "${GREEN}✓ Startup scripts created${NC}"
echo ""

# ---- DONE ----
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  QTOP NODE INSTALLATION COMPLETE!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "To start your node:"
echo -e "  ${YELLOW}~/qubit-topcoin/start_node.sh${NC}"
echo ""
echo -e "To use the wallet:"
echo -e "  ${YELLOW}~/qubit-topcoin/wallet.sh create${NC}"
echo -e "  ${YELLOW}~/qubit-topcoin/wallet.sh balance${NC}"
echo -e "  ${YELLOW}~/qubit-topcoin/wallet.sh send${NC}"
echo ""
echo -e "To open the block explorer:"
echo -e "  ${YELLOW}open ~/qubit-topcoin/explorer.html${NC}"
echo ""
echo -e "GitHub: github.com/Kstyle12/qubit-topcoin"
echo -e "Network: Cori Testnet"
echo ""
echo -e "${BLUE}Qubit TopCoin. For everyone. Forever.${NC}"
echo ""
