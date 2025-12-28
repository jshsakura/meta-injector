#!/usr/bin/env python3
"""
CC Patch Scraper with Undetected ChromeDriver
GBAtemp CC hacks 스레드에서 모든 CC 패치를 수집합니다.
"""
import re
import time
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "core" / "CCPatches"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# GBAtemp post URLs from the main thread
GAME_POSTS = {
    # Disc games
    "Animal Crossing: City Folk": "10507857",
    "Battleship": "10566403",
    "Bit.Trip Complete": "10521508",
    "Cars": "10584739",
    "Cars: Mater-National Championship": "10572842",
    "Cars Race-O-Rama": "10576852",
    "de Blob": "10512282",
    "de Blob 2": "10520139",
    "Despicable Me": "10571752",
    "Disney Universe": "10480811",
    "Donkey Kong Jungle Beat": "10495401",
    "Donkey Kong Country Returns": "10503137",
    "Dragon Ball Z: Budokai Tenkaichi 3": "10514682",
    "Endless Ocean": "10509770",
    "Epic Mickey": "10530193",
    "Excite Truck": "10484414",
    "Flip's Twisted World": "10557637",
    "Fortune Street": "10569144",
    "Fragile Dreams": "10550197",
    "Geon Cube": "10555935",
    "Kirby's Epic Yarn": "10490011",
    "Kirby's Return to Dream Land": "10544615",
    "Lego Batman": "10568257",
    "Lego Indiana Jones": "10562587",
    "Lego Indiana Jones 2": "10582179",
    "Lego Star Wars Complete Saga": "10557637",
    "Little King's Story": "10479517",  # First post
    "Lost in Shadow": "10562040",
    "Madagascar Escape 2 Africa": "10486052",
    "Mario Kart Wii": "10520779",
    "Mario Sports Mix": "10517717",
    "Mario Strikers Charged": "10561194",
    "Metroid Other M": "10491796",
    "Monster Hunter G": "10587603",
    "Mushroom Men The Spore Wars": "10545597",
    "MySims Agents": "10553562",
    "Namco Museum Megamix": "10483441",
    "New Super Mario Bros Wii": "10533824",
    "Punch-Out!!": "10520139",
    "Resident Evil 4": "10495957",
    "Rise of the Guardians": "10563275",
    "Rhythm Heaven Fever": "10516135",
    "Rygar The Battle of Argus": "10567362",
    "The Simpsons Game": "10554367",
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

# Known game IDs for some games (to help parsing)
KNOWN_GAME_IDS = {
    "Animal Crossing": ["RUUE01", "RUUP01", "RUUJ01", "RUUK01"],
    "Donkey Kong Country Returns": ["SFTE01", "SFTP01", "SFTJ01"],
    "Kirby's Epic Yarn": ["RKEE01", "RKEP01", "RKEJ01", "RLEK01"],
    "Little King's Story": ["ROUE5G", "ROEP5G", "ROUJ5G"],
    "Mario Kart Wii": ["RMCE01", "RMCP01", "RMCJ01", "RMCK01"],
    "Metroid Other M": ["R3OE01", "R3OP01", "R3OJ01"],
    "New Super Mario Bros Wii": ["SMNE01", "SMNP01", "SMNJ01", "SMNK01"],
    "Rhythm Heaven Fever": ["SOME01", "SOMP01", "SOMJ01", "SOMK01"],
    "Super Paper Mario": ["R8PE01", "R8PP01", "R8PJ01"],
    "Wario Land Shake It": ["RWLE01", "RWLP01", "RWLJ01", "RWLK01"],
}


def txt_to_gct(game_id: str, codes: List[str], output_path: Path) -> bool:
    """Convert text Gecko codes to GCT binary format."""
    try:
        # GCT header
        gct_data = bytearray.fromhex("00D0C0DE00D0C0DE")
        
        for code_line in codes:
            # Clean code line
            code_line = code_line.strip()
            if not code_line or code_line.startswith("#") or code_line.startswith("*"):
                continue
            
            # Remove any non-hex characters except space
            code_line = re.sub(r'[^0-9A-Fa-f\s]', '', code_line)
            
            # Split by spaces and process each pair
            parts = code_line.split()
            for part in parts:
                if len(part) >= 8:
                    # Each code is 8 hex digits = 4 bytes
                    try:
                        gct_data += bytearray.fromhex(part[:8])
                    except ValueError:
                        continue
        
        # GCT footer
        gct_data += bytearray.fromhex("F000000000000000")
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(gct_data)
        
        print(f"  ✓ Created: {output_path.name} ({len(gct_data)} bytes)")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to create GCT for {game_id}: {e}")
        return False


def extract_codes_from_html(html_content: str) -> Dict[str, List[str]]:
    """Extract Gecko codes from HTML content."""
    result = {}
    
    # Find code blocks
    code_pattern = r'<code[^>]*>(.*?)</code>'
    code_blocks = re.findall(code_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    # Also try pre blocks
    pre_pattern = r'<pre[^>]*>(.*?)</pre>'
    pre_blocks = re.findall(pre_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    all_blocks = code_blocks + pre_blocks
    
    for block in all_blocks:
        # Clean HTML entities
        block = block.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        block = re.sub(r'<[^>]+>', '', block)  # Remove HTML tags
        
        # Check if this looks like Gecko code (8-digit hex patterns)
        if re.search(r'[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8}', block):
            # Try to find game ID in the block or nearby
            game_id_match = re.search(r'([A-Z]{3}[EJPKW][0-9A-Z]{2})', block)
            if game_id_match:
                game_id = game_id_match.group(1)
            else:
                # Look for region indicators
                if 'USA' in block or 'NTSC-U' in block:
                    game_id = "USA_UNKNOWN"
                elif 'EUR' in block or 'PAL' in block:
                    game_id = "EUR_UNKNOWN"
                elif 'JAP' in block or 'JPN' in block:
                    game_id = "JPN_UNKNOWN"
                else:
                    game_id = "UNKNOWN"
            
            # Extract code lines
            lines = block.strip().split('\n')
            code_lines = []
            for line in lines:
                line = line.strip()
                # Skip comments and headers
                if line.startswith('*') or line.startswith('#'):
                    continue
                # Check if line looks like code
                if re.match(r'^[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8}', line):
                    # Extract just the hex pairs
                    hex_parts = re.findall(r'[0-9A-Fa-f]{8}', line)
                    if len(hex_parts) >= 2:
                        code_lines.append(f"{hex_parts[0]} {hex_parts[1]}")
            
            if code_lines and game_id not in result:
                result[game_id] = code_lines
    
    return result


def scrape_with_undetected_chrome():
    """Scrape GBAtemp using undetected-chromedriver."""
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("[ERROR] undetected-chromedriver not installed!")
        print("Run: pip install undetected-chromedriver selenium")
        return False
    
    collected_patches = {}
    
    try:
        print("[INFO] Starting undetected Chrome browser...")
        options = uc.ChromeOptions()
        options.add_argument("--disable-popup-blocking")
        
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 30)
        
        base_url = "https://gbatemp.net/threads/new-classic-controller-hacks.659837/post-"
        
        for game_name, post_id in GAME_POSTS.items():
            url = f"{base_url}{post_id}"
            print(f"\n[SCRAPING] {game_name} (post-{post_id})...")
            
            try:
                driver.get(url)
                time.sleep(3)  # Wait for Cloudflare
                
                # Wait for content to load
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "message-content")))
                
                # Get page source
                html = driver.page_source
                
                # Extract codes
                codes = extract_codes_from_html(html)
                
                if codes:
                    for game_id, code_lines in codes.items():
                        if game_id not in collected_patches:
                            collected_patches[game_id] = {
                                "game_name": game_name,
                                "codes": code_lines,
                                "source": url
                            }
                            
                            # Create GCT file
                            gct_path = OUTPUT_DIR / f"{game_id}.gct"
                            txt_to_gct(game_id, code_lines, gct_path)
                    
                    print(f"  ✓ Found {len(codes)} region codes")
                else:
                    print(f"  - No codes found")
                
                time.sleep(2)  # Be polite
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        driver.quit()
        
    except Exception as e:
        print(f"[ERROR] Browser error: {e}")
        return False
    
    # Save metadata
    metadata_path = OUTPUT_DIR / "cc_patches_metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(collected_patches, f, indent=2, ensure_ascii=False)
    
    print(f"\n[DONE] Collected {len(collected_patches)} patches")
    print(f"[INFO] Metadata saved to {metadata_path}")
    
    return True


def parse_saved_html():
    """Parse the saved HTML file from the user."""
    saved_html = OUTPUT_DIR / "New Classic Controller Hacks _ GBAtemp.net - The Independent Video Game Community.html"
    
    if not saved_html.exists():
        print(f"[ERROR] Saved HTML not found: {saved_html}")
        return False
    
    print(f"[INFO] Parsing saved HTML: {saved_html}")
    
    with open(saved_html, 'r', encoding='utf-8') as f:
        html = f.read()
    
    codes = extract_codes_from_html(html)
    
    print(f"[INFO] Found {len(codes)} code blocks in saved HTML")
    
    for game_id, code_lines in codes.items():
        print(f"  - {game_id}: {len(code_lines)} lines")
        gct_path = OUTPUT_DIR / f"{game_id}.gct"
        txt_to_gct(game_id, code_lines, gct_path)
    
    return True


def main():
    print("=" * 60)
    print("CC Patch Scraper with Undetected ChromeDriver")
    print("=" * 60)
    
    # First try to parse the saved HTML
    print("\n[1] Parsing saved HTML file...")
    parse_saved_html()
    
    # Then try full scraping
    print("\n[2] Starting browser scraping...")
    print("    NOTE: Chrome will open and navigate to GBAtemp.")
    print("    Please wait for Cloudflare checks to complete.")
    
    choice = input("\nProceed with browser scraping? (y/n): ").strip().lower()
    if choice == 'y':
        scrape_with_undetected_chrome()
    else:
        print("[INFO] Skipping browser scraping")
    
    print("\n[DONE] Check core/CCPatches/ for GCT files")


if __name__ == "__main__":
    main()
