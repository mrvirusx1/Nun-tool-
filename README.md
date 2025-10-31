# NUN-Tool v2 (Menu-driven build with full scraper)

## What is this?
Safe, menu-driven Termux tool with an ethical public-info scraper.
This package contains the menu launcher `nun_tool.py`, the scraper `nun_scraper.py`,
NOTICE and license, plus an installer script that installs dependencies and can
create a Termux launcher.

## Quick install (Termux)
unzip NUN-Tool_v2.zip -d ~/
cd ~/NUN-Tool_v2
bash install.sh
# After installer completes (if running in Termux and permitted):
nun-tool

## If not using Termux
You can still run the tool locally:
python3 nun_tool.py

## Dependencies
- Python 3
- requests
- beautifulsoup4
- tldextract
- python-dateutil
