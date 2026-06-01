#!/bin/bash
# NetMHC Pipeline Master Script
# Complete epitope prediction workflow in one command

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "🧬 NetMHC Epitope Prediction Pipeline"
echo "====================================="
echo "Project: Vaccinology - SARS-CoV-2 S1 Analysis"
echo "Location: $(pwd)"
echo ""

# Check if epitope files exist
if [ ! -d "epitope_files_for_iedb/batch_submission_files" ]; then
    echo "❌ Epitope batch files not found!"
    echo "   Run epitope generation first"
    exit 1
fi

BATCH_COUNT=$(find epitope_files_for_iedb/batch_submission_files -name "*.txt" -not -name "*INSTRUCTIONS*" | wc -l)
echo "📁 Found $BATCH_COUNT batch files for processing"

# Check NetMHC installation
if [ ! -f "tools/netmhc/netmhcpan" ]; then
    echo ""
    echo "🔧 NetMHC tools not installed. Running setup..."
    bash scripts/setup_local_netmhc.sh

    if [ $? -ne 0 ]; then
        echo "❌ Setup failed. Check download requirements:"
        cat tools/netmhc/DOWNLOAD_INSTRUCTIONS.md
        exit 1
    fi
else
    echo "✅ NetMHC tools found"
fi

# Activate NetMHC tools
echo ""
echo "⚙️  Activating NetMHC environment..."
source scripts/activate_netmhc.sh

# Verify tools work
if ! netmhcpan -h >/dev/null 2>&1; then
    echo "❌ NetMHCpan not working"
    exit 1
fi

if ! netmhcIIpan -h >/dev/null 2>&1; then
    echo "❌ NetMHCIIpan not working"
    exit 1
fi

echo "✅ NetMHC tools verified and ready"

# Run predictions
echo ""
echo "🚀 Starting epitope predictions..."
echo "   Input: 4,274 SARS-CoV-2 S1 epitope candidates"
echo "   HLA Alleles: 11 MHC-I + 8 MHC-II (global coverage)"
echo "   Expected time: 10-20 minutes"
echo ""

python scripts/run_local_predictions.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 NetMHC Pipeline Complete!"
    echo "=========================="
    echo "📊 Results: results/netmhc_local/"
    echo "📈 Summary: results/netmhc_local/processing_summary.csv"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Review strong binders in CSV files"
    echo "   2. Run VaxiJen antigenicity analysis"
    echo "   3. Apply AllerTop safety filtering"
    echo "   4. Calculate population coverage"
    echo "   5. Design multi-epitope construct"
    echo ""
    echo "🚀 Ready for Stage 03 of vaccine pipeline!"
else
    echo ""
    echo "❌ Pipeline failed. Check errors above."
    exit 1
fi