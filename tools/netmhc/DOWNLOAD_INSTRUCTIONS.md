# NetMHC Tools Download Instructions

## Required Downloads (Academic License - Free)

### 1. NetMHCpan-4.2c (MHC-I Predictions) - LATEST VERSION ⭐
- **URL:** https://services.healthtech.dtu.dk/services/NetMHCpan-4.1/ (redirects to latest)
- **Steps:**
  1. Click "Download"
  2. Fill out academic license form
  3. **RECOMMENDED:** Download `netMHCpan-4.2c.Linux.tar.gz` (works on Windows Git Bash)
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
├── netMHCpan-4.2c.Linux.tar.gz (LATEST - recommended)
└── netMHCIIpan-4.0.Linux.tar.gz
```

**Note:** Setup script automatically detects NetMHCpan versions 4.1, 4.2c, or newer.
