#!/usr/bin/env bash
set -e
# NUN-Tool v2 installer: installs dependencies and optionally creates a Termux launcher
echo "NUN-Tool v2 installer starting..."
# Ensure in the folder with the files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

read -p "Install Python (pkg install python -y) if missing? [Y/n]: " resp
resp=${resp:-Y}
if [[ "$resp" =~ ^[Yy]$ ]]; then
  if ! command -v python >/dev/null 2>&1; then
    echo "Installing python..."
    pkg update -y || true
    pkg install python -y
  else
    echo "Python already installed."
  fi
fi

read -p "Install Python dependencies (requests, beautifulsoup4, tldextract, python-dateutil)? [Y/n]: " resp2
resp2=${resp2:-Y}
if [[ "$resp2" =~ ^[Yy]$ ]]; then
  if command -v pip >/dev/null 2>&1; then
    pip install --upgrade pip
    pip install requests beautifulsoup4 tldextract python-dateutil
  else
    echo "pip not found; attempting to use pip3..."
    pip3 install --upgrade pip
    pip3 install requests beautifulsoup4 tldextract python-dateutil
  fi
fi

# Offer to install Termux launcher
if [ -d "/data/data/com.termux/files" ]; then
  read -p "Create Termux launcher (install to /data/data/com.termux/files/usr)? [Y/n]: " resp3
  resp3=${resp3:-Y}
  if [[ "$resp3" =~ ^[Yy]$ ]]; then
    INSTALL_DIR="/data/data/com.termux/files/usr/share/nun-tool"
    BIN_DIR="/data/data/com.termux/files/usr/bin"
    mkdir -p "${INSTALL_DIR}"
    cp -f nun_tool.py nun_scraper.py NOTICE.txt LICENSE README.md "${INSTALL_DIR}/"
    mkdir -p "${BIN_DIR}"
    cat > "${BIN_DIR}/nun-tool" <<'EOF'
#!/usr/bin/env bash
echo -e "\\033[1;31m========================================\\033[0m"
echo -e "\\033[1;36m     🔰 NUN Anonymoushackeradmin 🔰\\033[0m"
echo -e "\\033[1;31m========================================\\033[0m"
echo -e "\\033[1;36mLaunching NUN Scraper Tool...\\033[0m"
python "${INSTALL_DIR}/nun_tool.py" "$@"
EOF
    chmod +x "${BIN_DIR}/nun-tool"
    chmod +x "${INSTALL_DIR}/nun_tool.py"
    chmod +x "${INSTALL_DIR}/nun_scraper.py"
    echo "Launcher installed at ${BIN_DIR}/nun-tool"
  fi
else
  echo "Not running inside Termux; skipping launcher install."
fi

echo "Installation complete. Run 'nun-tool' (if installed) or 'python nun_tool.py' to start."
