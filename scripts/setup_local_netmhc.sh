#!/bin/bash
# NetMHC Local Installation Script
# Platform: Windows (Git Bash), Linux, macOS
# Purpose: Reproducible NetMHC setup for epitope prediction

set -e  # Exit on any error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TOOLS_DIR="$PROJECT_DIR/tools/netmhc"

echo "🧬 NetMHC Local Setup - Reproducible Installation"
echo "=================================================="
echo "Project: $(basename "$PROJECT_DIR")"
echo "Platform: $(uname -s)"
echo "Tools will be installed to: $TOOLS_DIR"
echo ""

# Create tools directory
mkdir -p "$TOOLS_DIR"
cd "$TOOLS_DIR"

echo "📁 Created tools directory: $TOOLS_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."
MISSING_DEPS=()

if ! command_exists curl && ! command_exists wget; then
    MISSING_DEPS+=("curl or wget")
fi

if ! command_exists tar; then
    MISSING_DEPS+=("tar")
fi

if ! command_exists python3 && ! command_exists python; then
    MISSING_DEPS+=("python3")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "❌ Missing dependencies: ${MISSING_DEPS[*]}"
    echo "Please install these and re-run the script."
    exit 1
fi

echo "✅ All dependencies found"

# Create download instructions
cat > "$TOOLS_DIR/DOWNLOAD_INSTRUCTIONS.md" << 'EOF'
# NetMHC Tools Download Instructions

## Required Downloads (Academic License - Free)

### 1. NetMHCpan-4.1 (MHC-I Predictions)
- **URL:** https://services.healthtech.dtu.dk/services/NetMHCpan-4.1/
- **Steps:**
  1. Click "Download"
  2. Fill out academic license form
  3. Download: `netMHCpan-4.1.Linux.tar.gz` (Linux/macOS) or `netMHCpan-4.1.Windows.tar.gz` (Windows)
  4. Save to: `tools/netmhc/downloads/`

### 2. NetMHCIIpan-4.0 (MHC-II Predictions)
- **URL:** https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.0/
- **Steps:**
  1. Register and download
  2. Download: `netMHCIIpan-4.0.Linux.tar.gz` or `netMHCIIpan-4.0.Windows.tar.gz`
  3. Save to: `tools/netmhc/downloads/`

## After Download
Run: `bash scripts/setup_local_netmhc.sh` to complete installation.

## File Structure Expected:
```
tools/netmhc/downloads/
├── netMHCpan-4.1.Linux.tar.gz (or Windows variant)
└── netMHCIIpan-4.0.Linux.tar.gz (or Windows variant)
```
EOF

# Create downloads directory
mkdir -p downloads
echo "📋 Download instructions created: $TOOLS_DIR/DOWNLOAD_INSTRUCTIONS.md"

# Check if download files exist
NETMHCPAN_FILE=""
NETMHCIIPAN_FILE=""

# Look for NetMHCpan files (4.1 or 4.2)
for file in downloads/netMHCpan-4.*.tar.gz; do
    if [ -f "$file" ]; then
        NETMHCPAN_FILE="$file"
        break
    fi
done

# Look for NetMHCIIpan files
for file in downloads/netMHCIIpan-4.0*.tar.gz; do
    if [ -f "$file" ]; then
        NETMHCIIPAN_FILE="$file"
        break
    fi
done

if [ -z "$NETMHCPAN_FILE" ] || [ -z "$NETMHCIIPAN_FILE" ]; then
    echo ""
    echo "📥 DOWNLOAD REQUIRED"
    echo "===================="
    echo "Please download the NetMHC tools first:"
    echo ""
    cat "$TOOLS_DIR/DOWNLOAD_INSTRUCTIONS.md"
    echo ""
    echo "After downloading, run this script again."
    exit 0
fi

echo "✅ Found download files:"
echo "  - NetMHCpan: $NETMHCPAN_FILE"
echo "  - NetMHCIIpan: $NETMHCIIPAN_FILE"

# Extract tools
echo ""
echo "📦 Extracting tools..."

if [ -f "$NETMHCPAN_FILE" ]; then
    echo "Extracting NetMHCpan..."
    tar -xzf "$NETMHCPAN_FILE"
    echo "✅ NetMHCpan extracted"
fi

if [ -f "$NETMHCIIPAN_FILE" ]; then
    echo "Extracting NetMHCIIpan..."
    tar -xzf "$NETMHCIIPAN_FILE"
    echo "✅ NetMHCIIpan extracted"
fi

# Find extracted directories
NETMHCPAN_DIR=""
NETMHCIIPAN_DIR=""

for dir in netMHCpan-4.*/ ; do
    if [ -d "$dir" ]; then
        NETMHCPAN_DIR="$dir"
        break
    fi
done

for dir in netMHCIIpan-4.0*/ ; do
    if [ -d "$dir" ]; then
        NETMHCIIPAN_DIR="$dir"
        break
    fi
done

echo "Found directories:"
echo "  - NetMHCpan: $NETMHCPAN_DIR"
echo "  - NetMHCIIpan: $NETMHCIIPAN_DIR"

# Create wrapper scripts
echo ""
echo "🔧 Creating wrapper scripts..."

# NetMHCpan wrapper
cat > netmhcpan << EOF
#!/bin/bash
SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
"\$SCRIPT_DIR/${NETMHCPAN_DIR}netMHCpan" "\$@"
EOF
chmod +x netmhcpan

# NetMHCIIpan wrapper
cat > netmhcIIpan << EOF
#!/bin/bash
SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
"\$SCRIPT_DIR/${NETMHCIIPAN_DIR}netMHCIIpan" "\$@"
EOF
chmod +x netmhcIIpan

echo "✅ Wrapper scripts created"

# Create environment setup script
cat > "$PROJECT_DIR/scripts/activate_netmhc.sh" << EOF
#!/bin/bash
# Source this file to add NetMHC tools to PATH
# Usage: source scripts/activate_netmhc.sh

SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="\$(dirname "\$SCRIPT_DIR")"
NETMHC_TOOLS_DIR="\$PROJECT_DIR/tools/netmhc"

# Add NetMHC tools to PATH
export PATH="\$NETMHC_TOOLS_DIR:\$PATH"

echo "🧬 NetMHC tools activated"
echo "Tools directory: \$NETMHC_TOOLS_DIR"
echo ""
echo "Available commands:"
echo "  - netmhcpan    (MHC-I predictions)"
echo "  - netmhcIIpan  (MHC-II predictions)"
echo ""
echo "Test installation:"
echo "  netmhcpan -h"
echo "  netmhcIIpan -h"
EOF

echo "✅ Environment activation script created: scripts/activate_netmhc.sh"

# Test installation
echo ""
echo "🧪 Testing installation..."

# Add tools to current PATH
export PATH="$TOOLS_DIR:$PATH"

if ./netmhcpan -h > /dev/null 2>&1; then
    echo "✅ NetMHCpan working"
else
    echo "❌ NetMHCpan test failed"
fi

if ./netmhcIIpan -h > /dev/null 2>&1; then
    echo "✅ NetMHCIIpan working"
else
    echo "❌ NetMHCIIpan test failed"
fi

# Create .gitignore for tools
cat > "$TOOLS_DIR/.gitignore" << 'EOF'
# NetMHC downloaded files (large binaries)
downloads/*.tar.gz
netMHCpan-4.1*/
netMHCIIpan-4.0*/

# Keep wrapper scripts and documentation
!netmhcpan
!netmhcIIpan
!DOWNLOAD_INSTRUCTIONS.md
!.gitignore
!README.md
EOF

echo "✅ .gitignore created for tools directory"

echo ""
echo "🎉 NetMHC Local Installation Complete!"
echo "======================================"
echo ""
echo "📁 Installation location: $TOOLS_DIR"
echo "🔧 Wrapper scripts: netmhcpan, netmhcIIpan"
echo "⚙️  Activation script: scripts/activate_netmhc.sh"
echo ""
echo "🚀 Next Steps:"
echo "1. Activate tools: source scripts/activate_netmhc.sh"
echo "2. Test tools: netmhcpan -h && netmhcIIpan -h"
echo "3. Run epitope prediction: python scripts/run_local_predictions.py"
echo ""
echo "📝 Note: The actual tool binaries are .gitignored (they're large)"
echo "   Only setup scripts and documentation are committed to git"