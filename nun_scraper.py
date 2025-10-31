#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nun_scraper.py - Full public-info scraper (ethical, public-only)
# Author: NUN Anonymoushackeradmin
# Version: 1.0

import argparse
import json
import time
import re
import sys
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import tldextract
import urllib.robotparser
from datetime import datetime

USER_AGENT = "NUN-Tool-Scraper/1.2 (+https://example.invalid) Termux"

def polite_get(session, url, timeout=15, proxies=None):
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    resp = session.get(url, headers=headers, timeout=timeout, proxies=proxies)
    resp.raise_for_status()
    return resp

def check_robots_allowed(url, user_agent=USER_AGENT):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True

def extract_meta(soup):
    data = {}
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    if title:
        data["title"] = title
    for tag in soup.find_all(["meta"]):
        if tag.get("name"):
            data.setdefault("meta", {})[tag["name"].lower()] = tag.get("content", "")
        if tag.get("property"):
            data.setdefault("meta_prop", {})[tag["property"].lower()] = tag.get("content", "")
    jsonld = []
    for s in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            jsonld.append(json.loads(s.string))
        except Exception:
            continue
    if jsonld:
        data["json_ld"] = jsonld
    return data

def parse_generic(url, html):
    soup = BeautifulSoup(html, "html.parser")
    out = {"fetched_at": datetime.utcnow().isoformat() + "Z", "url": url}
    out.update(extract_meta(soup))
    texts = soup.stripped_strings
    sample = []
    for t in texts:
        if len(t) > 40:
            sample.append(t)
        if len(sample) >= 5:
            break
    out["text_sample"] = sample
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        links.append(href)
    out["links_count"] = len(links)
    out["links_sample"] = links[:10]
    return out

def parse_github(url, html):
    soup = BeautifulSoup(html, "html.parser")
    out = {"platform": "github", "url": url}
    name_tag = soup.find("span", {"class":"p-name"})
    if name_tag:
        out["name"] = name_tag.get_text(strip=True)
    bio = soup.find("div", {"class":"p-note"})
    if bio:
        out["bio"] = bio.get_text(strip=True)
    def find_count(label):
        el = soup.find("a", href=re.compile(rf".*{label}"))
        if el:
            t = el.get_text(strip=True)
            t = re.sub(r"\s+", " ", t)
            return t
    out["followers"] = find_count("followers")
    out["following"] = find_count("following")
    repos = []
    for repo in soup.select("div#user-repositories-list li"):
        rname = repo.find("a", itemprop="name codeRepository")
        if rname:
            repos.append(rname.get_text(strip=True))
        if len(repos) >= 5:
            break
    out["repos_sample"] = repos
    out.update(extract_meta(soup))
    out["fetched_at"] = datetime.utcnow().isoformat() + "Z"
    return out

def parse_reddit(url, html):
    soup = BeautifulSoup(html, "html.parser")
    out = {"platform": "reddit", "url": url}
    out.update(extract_meta(soup))
    m = re.search(r"(reddit\.com/(r/[^/]+|user/[^/]+))", url)
    if m:
        out["path_hint"] = m.group(1)
    posts = []
    for h in soup.find_all(["h3"]):
        txt = h.get_text(strip=True)
        if len(txt) > 20:
            posts.append(txt)
        if len(posts) >= 5:
            break
    out["posts_sample"] = posts
    out["fetched_at"] = datetime.utcnow().isoformat() + "Z"
    return out

PARSERS = {
    "generic": parse_generic,
    "github": parse_github,
    "reddit": parse_reddit,
}

def scrape(url, platform="generic", session=None, proxies=None, delay=1.2):
    if not session:
        session = requests.Session()
    allowed = check_robots_allowed(url)
    if not allowed:
        raise PermissionError(f"Robots.txt disallows scraping {url}")
    time.sleep(max(0, delay))
    resp = polite_get(session, url, proxies=proxies)
    html = resp.text
    parser = PARSERS.get(platform, parse_generic)
    return parser(url, html)

def cli_main():
    p = argparse.ArgumentParser(description="NUN Tool — Public Info Scraper (ethical use)")
    p.add_argument("--platform", default="generic", help="Platform parser: generic|github|reddit")
    p.add_argument("--url", required=True, help="Target public URL to scrape")
    p.add_argument("--out", default="results.json", help="Output filename (json)")
    p.add_argument("--delay", type=float, default=1.2, help="Seconds to sleep before request")
    p.add_argument("--proxy", default=None, help="Optional http(s) proxy (e.g. http://127.0.0.1:8080)")
    args = p.parse_args()

    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    try:
        out = scrape(args.url, platform=args.platform, session=session, proxies=proxies, delay=args.delay)
    except PermissionError as e:
        print(f"[!] Permission error: {e}", file=sys.stderr)
        sys.exit(2)
    except requests.HTTPError as e:
        print(f"[!] HTTP error: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(4)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved: {args.out}")

if __name__ == "__main__":
    cli_main()
