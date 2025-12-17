#!/usr/bin/env python3
"""
CC Patch Scraper using cloudscraper
GBAtemp CC hacks 스레드에서 모든 CC 패치를 수집합니다 (브라우저 없이).
"""
import re
import json
import time
from pathlib import Path

try:
    import cloudscraper
    from bs4 import BeautifulSoup
except ImportError:
    print("Required packages not installed!")
    print("Run: pip install cloudscraper beautifulsoup4 lxml")
    exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "core" / "CCPatches"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# All game post IDs from GBAtemp thread
GAME_POSTS = {
    "Animal Crossing City Folk": "10507857",
    "Battleship": "10566403",
    "Bit Trip Complete": "10521508",
    "Cars": "10584739",
    "Cars Mater-National": "10572842",
    "Cars Race-O-Rama": "10576852",
    "de Blob": "10512282",
    "de Blob 2": "10520139",
    "Despicable Me": "10571752",
    "Disney Universe": "10480811",
    "DK Jungle Beat": "10495401",
    "DK Country Returns": "10503137",
    "DBZ Budokai Tenkaichi 3": "10514682",
    "Endless Ocean": "10509770",
    "Epic Mickey": "10530193",
    "Excite Truck": "10484414",
    "Flips Twisted World": "10557637",
    "Fortune Street": "10569144",
    "Fragile Dreams": "10550197",
    "Geon Cube": "10555935",
    "Kirby Epic Yarn": "10490011",
    "Kirby Return to Dream Land": "10544615",
    "Lego Batman": "10568257",
    "Lego Indiana Jones": "10562587",
    "Lego Indiana Jones 2": "10582179",
    "Lego Star Wars Complete": "10557637",
    "Little Kings Story": "10479517",
    "Lost in Shadow": "10562040",
    "Madagascar 2": "10486052",
    "Mario Kart Wii": "10520779",
    "Mario Sports Mix": "10517717",
    "Mario Strikers Charged": "10561194",
    "Metroid Other M": "10491796",
    "Monster Hunter G": "10587603",
    "Mushroom Men": "10545597",
    "MySims Agents": "10553562",
    "Namco Museum Megamix": "10483441",
    "New Super Mario Bros Wii": "10533824",
    "Punch-Out": "10520139",
    "Resident Evil 4": "10495957",
    "Rise of the Guardians": "10563275",
    "Rhythm Heaven Fever": "10516135",
    "Rygar Battle of Argus": "10567362",
    "Simpsons Game": "10554367",
    "Speed Racer": "10499051",
    "Spider-Man Friend or Foe": "10560157",
    "SpongeBob Globs of Doom": "10578742",
    "Super Paper Mario": "10496857",
    "Tornado Outbreak": "10549949",
    "Toy Story 3": "10571174",
    "Tron Evolution": "10489330",
    "Wario Land Shake It": "10491236",
    # WiiWare
    "Alien Crush Returns": "10539315",
    "Blaster Master Overdrive": "10524746",
    "Fluidity": "10544022",
    "Jett Rocket": "10542014",
    "NyxQuest": "10558603",
    "Uno": "10557787",
}


def txt_to_gct(game_id: str, codes: list, output_path: Path) -> bool:
    """Convert text Gecko codes to GCT binary format."""
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
                    except ValueError:
                        continue
        
        gct_data += bytearray.fromhex("F000000000000000")
        
        with open(output_path, 'wb') as f:
            f.write(gct_data)
        return True
    except Exception as e:
        print(f"  Error creating GCT: {e}")
        return False


def extract_codes_from_post(html: str) -> dict:
    """Extract Gecko codes from a GBAtemp post."""
    soup = BeautifulSoup(html, 'lxml')
    results = {}
    
    # Find all code blocks
    code_blocks = soup.find_all('code')
    
    for block in code_blocks:
        text = block.get_text()
        
        # Find game ID in the text or nearby tab header
        game_id = None
        
        # Check parent elements for region tabs
        parent = block.find_parent('li', class_='bbCodeTabContent')
        if parent:
            tab_class = parent.get('class', [])
            # Look for tab index
        
        # Look for game ID pattern in code block
        id_matches = re.findall(r'\b([A-Z]{3}[EJPKW][0-9A-Z]{2})\b', text)
        
        if not id_matches:
            # Try to determine from tab headers
            tab_container = block.find_parent('div', class_='bbCodeTabs')
            if tab_container:
                tabs = tab_container.find_all('a', class_='bbCodeTab')
                current_tab = block.find_parent('li', class_='bbCodeTabContent')
                if current_tab and tabs:
                    try:
                        tab_index = list(tab_container.find_all('li', class_='bbCodeTabContent')).index(current_tab)
                        if tab_index < len(tabs):
                            region = tabs[tab_index].get_text().strip()
                            print(f"    Found region tab: {region}")
                    except:
                        pass
        
        # Extract code lines
        lines = text.strip().split('\n')
        code_lines = []
        
        for line in lines:
            line = line.strip()
            # Match Gecko code pattern: 8 hex digits, space, 8 hex digits
            if re.match(r'^[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8}', line):
                # Extract just the hex parts
                hex_match = re.findall(r'[0-9A-Fa-f]{8}', line)
                if len(hex_match) >= 2:
                    code_lines.append(f"{hex_match[0]} {hex_match[1]}")
        
        if code_lines:
            # Use found game ID or generate placeholder
            for gid in id_matches:
                if gid not in results:
                    results[gid] = code_lines
                    break
            else:
                # If no game ID found, use first found or skip
                if id_matches:
                    results[id_matches[0]] = code_lines
    
    return results


def main():
    print("=" * 60)
    print("CC Patch Scraper (cloudscraper)")
    print("=" * 60)
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    collected = {}
    failed = []
    
    total = len(GAME_POSTS)
    
    for i, (game_name, post_id) in enumerate(GAME_POSTS.items(), 1):
        url = f"https://gbatemp.net/threads/new-classic-controller-hacks.659837/post-{post_id}"
        print(f"\n[{i}/{total}] {game_name}...")
        
        try:
            response = scraper.get(url, timeout=30)
            
            if response.status_code == 200:
                codes = extract_codes_from_post(response.text)
                
                if codes:
                    for game_id, code_lines in codes.items():
                        gct_path = OUTPUT_DIR / f"{game_id}.gct"
                        if txt_to_gct(game_id, code_lines, gct_path):
                            print(f"  ✓ {game_id}: {len(code_lines)} lines -> {gct_path.name}")
                            collected[game_id] = {
                                "game": game_name,
                                "lines": len(code_lines),
                                "post": post_id
                            }
                else:
                    print(f"  - No codes extracted")
                    failed.append(game_name)
            else:
                print(f"  ✗ HTTP {response.status_code}")
                failed.append(game_name)
            
            # Be polite - wait between requests
            time.sleep(2)
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed.append(game_name)
    
    # Save metadata
    metadata = {
        "collected": collected,
        "failed": failed,
        "total_patches": len(collected)
    }
    
    metadata_path = OUTPUT_DIR / "cc_patches_metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"DONE: Collected {len(collected)} patches from {total} games")
    print(f"Failed: {len(failed)} games")
    if failed:
        print(f"  {', '.join(failed[:10])}" + ("..." if len(failed) > 10 else ""))
    print(f"\nMetadata saved to: {metadata_path}")
    print(f"GCT files in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
