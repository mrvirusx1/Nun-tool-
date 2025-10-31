#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nun_tool.py - Menu-driven launcher for NUN Tool (uses nun_scraper.py)
# Author: NUN Anonymoushackeradmin

import os, sys, time, subprocess, shutil

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPER = os.path.join(THIS_DIR, "nun_scraper.py")
NOTICE = os.path.join(THIS_DIR, "NOTICE.txt")
FB_PROFILE = "https://www.facebook.com/profile.php?id=61582396620144&mibextid=ZbWKwL"

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def banner():
    clear()
    print("\\033[1;31m========================================\\033[0m")
    print("\\033[1;36m     🔰 NUN Anonymoushackeradmin 🔰\\033[0m")
    print("\\033[1;31m========================================\\033[0m")
    print("\\033[1;36m NUN Tool — Public-info scraper (ethical)\\033[0m")
    print()

def show_notice():
    if os.path.exists(NOTICE):
        try:
            with open(NOTICE, "r", encoding="utf-8") as f:
                print(f.read())
        except Exception:
            pass
    else:
        print("NOTICE.txt not found.")

def open_url(url):
    if shutil.which("termux-open-url"):
        os.system(f'termux-open-url "{url}"')
    elif shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", url])
    else:
        print(url)

def run_scrape_cli(platform=None):
    url = input("Target public URL: ").strip()
    if not url:
        print("URL required.")
        return
    plat = platform or input("Platform (generic|github|reddit) [generic]: ").strip() or "generic"
    out = input("Output filename [results.json]: ").strip() or "results.json"
    delay = input("Delay seconds [1.2]: ").strip() or "1.2"
    proxy = input("Proxy (http://host:port) [none]: ").strip() or None
    cmd = [sys.executable, SCRAPER, "--platform", plat, "--url", url, "--out", out, "--delay", delay]
    if proxy:
        cmd += ["--proxy", proxy]
    print("\\n[+] Running scraper...")
    subprocess.call(cmd)
    input("\\nPress Enter to continue...")

def main_menu():
    while True:
        banner()
        print("1) Show NOTICE / Follow author")
        print("2) Scrape a public URL (generic)")
        print("3) Scrape GitHub profile")
        print("4) Scrape Reddit page")
        print("5) Open Facebook profile")
        print("6) Exit")
        choice = input("\\nChoose: ").strip()
        if choice == "1":
            clear()
            show_notice()
            input("\\nPress Enter to continue...")
        elif choice == "2":
            run_scrape_cli("generic")
        elif choice == "3":
            run_scrape_cli("github")
        elif choice == "4":
            run_scrape_cli("reddit")
        elif choice == "5":
            open_url(FB_PROFILE)
            input("\\nPress Enter to continue...")
        elif choice == "6":
            print("Exiting...")
            time.sleep(0.5)
            break
        else:
            print("Invalid choice.")
            time.sleep(0.6)

if __name__ == "__main__":
    main_menu()
