#!/bin/bash

# =========================================
#   QTP Node — Linux Service Setup
#   Run this after install.sh
# =========================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  QTP NODE SERVICE SETUP${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "This script is for Linux servers only."
    echo "On Mac, just run: ~/qubit-topcoin/start_node.sh"
    exit 1
fi

USER=$(whoami)
HOME_DIR=$(eval echo ~$USER)

echo -e "Setting up service for user: ${YELLOW}$USER${NC}"
echo -e "Home directory: ${YELLOW}$HOME_DIR${NC}"
echo ""

# Create the service file
sudo tee /etc/systemd/system/qtp-node.service > /dev/null << SERVICE
[Unit]
Description=Qubit TopCoin (QTP) Node - Cori Testnet
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME_DIR/qubit-topcoin/qtpcore
ExecStart=$HOME_DIR/qubit-topcoin/qtpcore/target/release/qtpcore 5003
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=qtp-node
Environment=HOME=$HOME_DIR

[Install]
WantedBy=multi-user.target
SERVICE

echo -e "${GREEN}✓ Service file created${NC}"

# Reload systemd
sudo systemctl daemon-reload
echo -e "${GREEN}✓ Systemd reloaded${NC}"

# Enable service to start on boot
sudo systemctl enable qtp-node
echo -e "${GREEN}✓ Service enabled on boot${NC}"

# Start the service
sudo systemctl start qtp-node
echo -e "${GREEN}✓ Service started${NC}"

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  QTP NODE IS NOW RUNNING AS A SERVICE${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "Useful commands:"
echo -e "  ${YELLOW}sudo systemctl status qtp-node${NC}   — Check status"
echo -e "  ${YELLOW}sudo systemctl stop qtp-node${NC}     — Stop node"
echo -e "  ${YELLOW}sudo systemctl restart qtp-node${NC}  — Restart node"
echo -e "  ${YELLOW}sudo journalctl -u qtp-node -f${NC}   — View live logs"
echo ""
echo -e "Your node is running on port 5003"
echo -e "Check status: ${YELLOW}curl http://localhost:5003/status${NC}"
echo ""
echo -e "${BLUE}Qubit TopCoin. For everyone. Forever.${NC}"
echo ""
