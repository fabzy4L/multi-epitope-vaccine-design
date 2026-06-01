#!/bin/bash
# Source this file to add NetMHC tools to PATH
# Usage: source scripts/activate_netmhc.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
NETMHC_TOOLS_DIR="$PROJECT_DIR/tools/netmhc"

# Add NetMHC tools to PATH
export PATH="$NETMHC_TOOLS_DIR:$PATH"

echo "🧬 NetMHC tools activated"
echo "Tools directory: $NETMHC_TOOLS_DIR"
echo ""
echo "Available commands:"
echo "  - netmhcpan    (MHC-I predictions)"
echo "  - netmhcIIpan  (MHC-II predictions)"