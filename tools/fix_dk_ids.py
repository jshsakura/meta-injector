#!/usr/bin/env python3
"""
Fix DK Jungle Beat IDs and Refresh Mario Strikers
Resolves ID conflict where DKJB was mapped to Mario Strikers ID.
"""
import re
import json
import time
from pathlib import Path

try:
    import cloudscraper
    from bs4 import BeautifulSoup
except ImportError:
    print("Required packages not installed! (cloudscraper, bs4)")
    exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "core" / "CCPatches"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Correct Mapping
GAMES = {
    "Donkey Kong Jungle Beat": {
        "post_id": "10495401",
        "regions": {"USA": "R49E01", "EUR": "R49P01", "JPN": "R49J01"}
    },
    "Mario Strikers Charged": {
        "post_id": "10561194",
        "regions": {"USA": "R4QE01", "EUR": "R4QP01", "JPN": "R4QJ01", "KOR": "R4QK01"}
    }
}

def txt_to_gct(game_id: str, codes: list, output_path: Path) -> bool:
    try:
        gct_data = bytearray.fromhex("00D0C0DE00D0C0DE")
        for code_line in codes:
            code_line = code_line.strip()
            if not code_line or code_line.startswith("*") or code_line.startswith("#"):
                continue
            code_line = re.sub(r'[^0-9A-Fa-f\s]', '', code_line)
            parts = code_line.split()
            for part in parts:
                if len(part) >= 8:
                    try:
                        gct_data += bytearray.fromhex(part[:8])
                    except:
                        continue
        gct_data += bytearray.fromhex("F000000000000000")
        if len(gct_data) <= 24:
            return False
        with open(output_path, 'wb') as f:
            f.write(gct_data)
        return True
    except Exception as e:
        print(f"  Error GCT: {e}")
        return False

def extract_codes_by_region(html: str, game_info: dict) -> dict:
    soup = BeautifulSoup(html, 'lxml')
    results = {}
    regions = game_info.get("regions", {})
    region_names = {
        "USA": ["USA", "US", "NTSC-U", "America"],
        "EUR": ["Europe", "EUR", "PAL", "UK"],
        "JPN": ["Japan", "JPN", "JP", "NTSC-J"],
        "KOR": ["Korea", "KOR", "KR"]
    }
    
    # Try tabs
    tab_containers = soup.find_all('div', class_='bbCodeTabs')
    for tab_container in tab_containers:
        tabs = tab_container.find_all('a', class_='bbCodeTab')
        tab_contents = tab_container.find_all('li', class_='bbCodeTabContent')
        
        for i, (tab, content) in enumerate(zip(tabs, tab_contents)):
            tab_text = tab.get_text().strip()
            matched_region = None
            for region_key, region_aliases in region_names.items():
                for alias in region_aliases:
                    if alias.lower() in tab_text.lower():
                        matched_region = region_key
                        break
                if matched_region:
                    break
            
            if not matched_region:
                continue
            game_id = regions.get(matched_region)
            if not game_id:
                continue
            
            code_block = content.find('code')
            if not code_block:
                continue
            
            lines = [l.strip() for l in code_block.get_text().strip().split('\n')]
            code_lines = []
            for line in lines:
                if re.match(r'^[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8}', line):
                    parts = re.findall(r'[0-9A-Fa-f]{8}', line)
                    if len(parts) >= 2:
                        code_lines.append(f"{parts[0]} {parts[1]}")
            
            if code_lines and game_id not in results:
                results[game_id] = code_lines

    # Try all code blocks if no tabs worked
    if not results:
        for block in soup.find_all('code'):
            lines = [l.strip() for l in block.get_text().strip().split('\n')]
            code_lines = []
            for line in lines:
                if re.match(r'^[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8}', line):
                    parts = re.findall(r'[0-9A-Fa-f]{8}', line)
                    if len(parts) >= 2:
                        code_lines.append(f"{parts[0]} {parts[1]}")
            if code_lines:
                # Assign to first available ID not yet found
                for region_key, game_id in regions.items():
                    if game_id and game_id not in results:
                        results[game_id] = code_lines
                        break
    
    return results

def main():
    print("Fixing DK Jungle Beat and Mario Strikers...")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    collected = {}
    
    for game_name, game_info in GAMES.items():
        url = f"https://gbatemp.net/threads/new-classic-controller-hacks.659837/post-{game_info['post_id']}"
        print(f"Fetching {game_name} ({url})...")
        try:
            response = scraper.get(url, timeout=30)
            if response.status_code == 200:
                codes = extract_codes_by_region(response.text, game_info)
                if codes:
                    for game_id, code_lines in codes.items():
                        gct_path = OUTPUT_DIR / f"{game_id}.gct"
                        if txt_to_gct(game_id, code_lines, gct_path):
                            print(f"  ✓ {game_id}: {len(code_lines)} lines")
                            collected[game_id] = {"game": game_name, "lines": len(code_lines), "post": game_info['post_id']}
                else:
                    print(f"  - No codes found")
            else:
                print(f"  ✗ HTTP {response.status_code}")
            time.sleep(2)
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Update metadata
    meta_path = OUTPUT_DIR / "cc_patches_metadata.json"
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {"collected": {}, "failed": [], "total_patches": 0}
    
    metadata["collected"].update(collected)
    metadata["total_patches"] = len(metadata["collected"])
    
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nUpdated metadata. Total patches: {metadata['total_patches']}")

if __name__ == "__main__":
    main()
