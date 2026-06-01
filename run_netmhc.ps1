# NetMHC Pipeline Launcher for PowerShell
# Processes SARS-CoV-2 epitopes using local NetMHC tools

Write-Host "NetMHC Local Epitope Processor" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host ""

# Check if downloads exist
$downloadsPath = "tools\netmhc\downloads"
if (!(Test-Path $downloadsPath)) {
    Write-Host "ERROR: Downloads directory not found" -ForegroundColor Red
    Write-Host "Run setup script first" -ForegroundColor Yellow
    exit 1
}

$netmhcpan = Get-ChildItem "$downloadsPath\netMHCpan-*.tar.gz" -ErrorAction SilentlyContinue
$netmhciipan = Get-ChildItem "$downloadsPath\netMHCIIpan-*.tar.gz" -ErrorAction SilentlyContinue

if (!$netmhcpan -or !$netmhciipan) {
    Write-Host "ERROR: NetMHC tool files not found in downloads/" -ForegroundColor Red
    Write-Host "Expected files:" -ForegroundColor Yellow
    Write-Host "  - netMHCpan-4.2c.Linux.tar.gz"
    Write-Host "  - netMHCIIpan-4.0.Linux.tar.gz"
    exit 1
}

Write-Host "Found downloaded files:" -ForegroundColor Green
Write-Host "  - $($netmhcpan.Name)"
Write-Host "  - $($netmhciipan.Name)"
Write-Host ""

# Extract tools if needed
$toolsExtracted = $false

if (!(Test-Path "tools\netmhc\netmhcpan.exe") -and !(Test-Path "tools\netmhc\netmhcpan")) {
    Write-Host "Extracting NetMHC tools..." -ForegroundColor Yellow

    # Check if tar is available
    try {
        tar --version > $null
        Write-Host "Using system tar to extract files..."

        Push-Location "tools\netmhc"

        # Extract NetMHCpan
        Write-Host "Extracting $($netmhcpan.Name)..."
        tar -xzf "downloads\$($netmhcpan.Name)"

        # Extract NetMHCIIpan
        Write-Host "Extracting $($netmhciipan.Name)..."
        tar -xzf "downloads\$($netmhciipan.Name)"

        Pop-Location
        $toolsExtracted = $true
        Write-Host "Extraction complete!" -ForegroundColor Green

    } catch {
        Write-Host "ERROR: tar not available. Please use Git Bash instead:" -ForegroundColor Red
        Write-Host "  1. Right-click in project folder" -ForegroundColor Yellow
        Write-Host "  2. Select 'Git Bash Here'" -ForegroundColor Yellow
        Write-Host "  3. Run: ./run_netmhc_pipeline.sh" -ForegroundColor Yellow
        exit 1
    }
}

# Set environment variables for UTF-8 encoding
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Write-Host ""
Write-Host "Starting epitope predictions..." -ForegroundColor Green
Write-Host "This may take 10-20 minutes..." -ForegroundColor Yellow
Write-Host ""

# Run the prediction script with UTF-8 encoding
try {
    python scripts\run_local_predictions.py

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "SUCCESS: NetMHC processing complete!" -ForegroundColor Green
        Write-Host "Results saved to: results\netmhc_local\" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "  1. Review results in CSV files"
        Write-Host "  2. Run VaxiJen antigenicity analysis"
        Write-Host "  3. Apply AllerTop safety filtering"
        Write-Host "  4. Calculate population coverage"
    } else {
        Write-Host "ERROR: Processing failed. Check output above." -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Failed to run Python script" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}