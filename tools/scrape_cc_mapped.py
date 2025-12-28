#!/usr/bin/env python3
"""
CC Patch Collector with Game ID Mapping
Based on pearlfect's spreadsheet data
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

# Game ID mapping based on GameTDB and region codes
# Format: "Game Name": {"post_id": "xxx", "regions": {"USA": "GAMEID", "EUR": "GAMEID", "JPN": "GAMEID", "KOR": "GAMEID"}}
GAMES = {
    "Animal Crossing City Folk": {
        "post_id": "10507857",
        "regions": {"USA": "RUUE01", "EUR": "RUUP01", "JPN": "RUUJ01", "KOR": "RUUK01"}
    },
    "Battleship": {
        "post_id": "10566403",
        "regions": {"USA": "SBTE52", "EUR": "SBTX52"}
    },
    "Bit Trip Complete": {
        "post_id": "10521508",
        "regions": {"USA": "SBIE01", "EUR": "SBIP01"}
    },
    "Cars": {
        "post_id": "10584739",
        "regions": {"USA": "RC2E78", "EUR": "RC2P78", "JPN": "RC2J78"}
    },
    "Cars Mater-National": {
        "post_id": "10572842",
        "regions": {"USA": "RCME78", "EUR": "RCMP78"}
    },
    "Cars Race-O-Rama": {
        "post_id": "10576852",
        "regions": {"USA": "RRCE78", "EUR": "RRCP78"}
    },
    "de Blob": {
        "post_id": "10512282",
        "regions": {"USA": "R8BE78", "EUR": "R8BP78", "JPN": "R8BJ78", "KOR": "R8BK78"}
    },
    "de Blob 2": {
        "post_id": "10520139",
        "regions": {"USA": "SDBE78", "EUR": "SDBP78"}
    },
    "Despicable Me": {
        "post_id": "10571752",
        "regions": {"USA": "SDME78", "EUR": "SDMP78"}
    },
    "Disney Universe": {
        "post_id": "10480811",
        "regions": {"USA": "SDXE4Q", "EUR": "SDXP4Q"}
    },
    "DK Jungle Beat": {
        "post_id": "10495401",
        "regions": {"USA": "R4QE01", "EUR": "R4QP01", "JPN": "R4QJ01"}
    },
    "DK Country Returns": {
        "post_id": "10503137",
        "regions": {"USA": "SF8E01", "EUR": "SF8P01", "JPN": "SF8J01"}
    },
    "DBZ Budokai Tenkaichi 3": {
        "post_id": "10514682",
        "regions": {"USA": "RDZE70", "EUR": "RDZP70", "JPN": "RDSJ70"}
    },
    "Endless Ocean": {
        "post_id": "10509770",
        "regions": {"USA": "RFBE01", "EUR": "RFBP01", "JPN": "RFBJ01"}
    },
    "Epic Mickey": {
        "post_id": "10530193",
        "regions": {"USA": "SEME4Q", "EUR": "SEMP4Q", "JPN": "SEMJ4Q"}
    },
    "Excite Truck": {
        "post_id": "10484414",
        "regions": {"USA": "REXE01", "EUR": "REXP01", "JPN": "REXJ01"}
    },
    "Flips Twisted World": {
        "post_id": "10557637",
        "regions": {"USA": "SFZE5G"}
    },
    "Fortune Street": {
        "post_id": "10569144",
        "regions": {"USA": "ST7E01", "EUR": "ST7P01", "JPN": "ST7J01"}
    },
    "Fragile Dreams": {
        "post_id": "10550197",
        "regions": {"USA": "R2GE01", "EUR": "R2GP01", "JPN": "R2GJ01"}
    },
    "Geon Cube": {
        "post_id": "10555935",
        "regions": {"USA": "RGCE20"}
    },
    "Kirby Epic Yarn": {
        "post_id": "10490011",
        "regions": {"USA": "RKEE01", "EUR": "RKEP01", "JPN": "RKEJ01", "KOR": "RLEK01"}
    },
    "Kirby Return to Dream Land": {
        "post_id": "10544615",
        "regions": {"USA": "SUKE01", "EUR": "SUKP01", "JPN": "SUKJ01"}
    },
    "Lego Batman": {
        "post_id": "10568257",
        "regions": {"USA": "RLBEWB", "EUR": "RLBPWR"}
    },
    "Lego Indiana Jones": {
        "post_id": "10562587",
        "regions": {"USA": "RLIELA", "EUR": "RLIPLA"}
    },
    "Lego Indiana Jones 2": {
        "post_id": "10582179",
        "regions": {"USA": "RL2EWR", "EUR": "RL2PWR"}
    },
    "Lego Star Wars Complete": {
        "post_id": "10557637",
        "regions": {"USA": "RLGEWR", "EUR": "RLGPWR", "JPN": "RLGJWR"}
    },
    "Little Kings Story": {
        "post_id": "10479517",
        "regions": {"USA": "ROUE5G", "EUR": "ROEP5G", "JPN": "ROUJ5G"}
    },
    "Lost in Shadow": {
        "post_id": "10562040",
        "regions": {"USA": "SDWE18", "EUR": "SDWP18", "JPN": "SDWJ18"}
    },
    "Madagascar 2": {
        "post_id": "10486052",
        "regions": {"USA": "RRGP52", "EUR": "RRGE52"}
    },
    "Mario Kart Wii": {
        "post_id": "10520779",
        "regions": {"USA": "RMCE01", "EUR": "RMCP01", "JPN": "RMCJ01", "KOR": "RMCK01"}
    },
    "Mario Sports Mix": {
        "post_id": "10517717",
        "regions": {"USA": "RMXE01", "EUR": "RMXP01", "JPN": "RMXJ01"}
    },
    "Mario Strikers Charged": {
        "post_id": "10561194",
        "regions": {"USA": "R4QE01", "EUR": "R4QP01", "JPN": "R4QJ01", "KOR": "R4QK01"}
    },
    "Metroid Other M": {
        "post_id": "10491796",
        "regions": {"USA": "R3OE01", "EUR": "R3OP01", "JPN": "R3OJ01"}
    },
    "Monster Hunter G": {
        "post_id": "10587603",
        "regions": {"JPN": "ROMJ08"}
    },
    "Mushroom Men": {
        "post_id": "10545597",
        "regions": {"USA": "RMMESJ", "EUR": "RMMPSJ"}
    },
    "MySims Agents": {
        "post_id": "10553562",
        "regions": {"USA": "R5QE69", "EUR": "R5QP69", "JPN": "R5QJ69"}
    },
    "Namco Museum Megamix": {
        "post_id": "10483441",
        "regions": {"USA": "SNME52"}
    },
    "New Super Mario Bros Wii": {
        "post_id": "10533824",
        "regions": {"USA": "SMNE01", "EUR": "SMNP01", "JPN": "SMNJ01", "KOR": "SMNK01"}
    },
    "Punch-Out": {
        "post_id": "10520139",
        "regions": {"USA": "RPWE01", "EUR": "RPWP01", "JPN": "RPWJ01"}
    },
    "Resident Evil 4": {
        "post_id": "10495957",
        "regions": {"USA": "RB4E08", "EUR": "RB4P08", "JPN": "RB4J08"}
    },
    "Rise of the Guardians": {
        "post_id": "10563275",
        "regions": {"USA": "SR9ED3", "EUR": "SR9PD3"}
    },
    "Rhythm Heaven Fever": {
        "post_id": "10516135",
        "regions": {"USA": "SOME01", "EUR": "SOMP01", "JPN": "SOMJ01", "KOR": "SOMK01"}
    },
    "Rygar Battle of Argus": {
        "post_id": "10567362",
        "regions": {"USA": "RY9E99", "EUR": "RY9P99", "JPN": "RY9J99"}
    },
    "Simpsons Game": {
        "post_id": "10554367",
        "regions": {"USA": "RSHE69", "EUR": "RSHP69"}
    },
    "Speed Racer": {
        "post_id": "10499051",
        "regions": {"USA": "R9PE52", "EUR": "R9PP52", "JPN": "R9PJ52"}
    },
    "Spider-Man Friend or Foe": {
        "post_id": "10560157",
        "regions": {"USA": "RSBF52", "EUR": "RSBP52"}
    },
    "SpongeBob Globs of Doom": {
        "post_id": "10578742",
        "regions": {"USA": "RSGE78", "EUR": "RSGP78", "KOR": "RSGK78"}
    },
    "Super Paper Mario": {
        "post_id": "10496857",
        "regions": {"USA": "R8PE01", "EUR": "R8PP01", "JPN": "R8PJ01", "KOR": "R8PK01"}
    },
    "Tornado Outbreak": {
        "post_id": "10549949",
        "regions": {"USA": "RTOE70", "EUR": "RTOP70"}
    },
    "Toy Story 3": {
        "post_id": "10571174",
        "regions": {"USA": "STSE4Q", "EUR": "STSP4Q"}
    },
    "Tron Evolution": {
        "post_id": "10489330",
        "regions": {"USA": "STRE4Q", "EUR": "STRP4Q"}
    },
    "Wario Land Shake It": {
        "post_id": "10491236",
        "regions": {"USA": "RWLE01", "EUR": "RWLP01", "JPN": "RWLJ01", "KOR": "RWLK01"}
    },
    # WiiWare
    "Alien Crush Returns": {
        "post_id": "10539315",
        "regions": {"USA": "WALE", "EUR": "WALP", "JPN": "WALJ"}
    },
    "Blaster Master Overdrive": {
        "post_id": "10524746",
        "regions": {"USA": "WBME", "EUR": "WBMP"}
    },
    "Fluidity": {
        "post_id": "10544022",
        "regions": {"USA": "WFLE", "EUR": "WFLP"}
    },
    "Jett Rocket": {
        "post_id": "10542014",
        "regions": {"USA": "WJRE", "EUR": "WJRP"}
    },
    "NyxQuest": {
        "post_id": "10558603",
        "regions": {"USA": "WNYE", "EUR": "WNYP", "JPN": "WNYJ"}
    },
    "Uno": {
        "post_id": "10557787",
        "regions": {"USA": "WU7E", "EUR": "WU7P", "JPN": "WU7J"}
    },
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
        
        if len(gct_data) <= 24:  # Just header + footer, no actual code
            return False
            
        with open(output_path, 'wb') as f:
            f.write(gct_data)
        return True
    except Exception as e:
        print(f"  Error creating GCT: {e}")
        return False


def extract_codes_by_region(html: str, game_info: dict) -> dict:
    """Extract Gecko codes from a GBAtemp post and map to game IDs."""
    soup = BeautifulSoup(html, 'lxml')
    results = {}
    
    regions = game_info.get("regions", {})
    region_names = {
        "USA": ["USA", "US", "NTSC-U", "America"],
        "EUR": ["Europe", "EUR", "PAL", "UK"],
        "JPN": ["Japan", "JPN", "JP", "NTSC-J"],
        "KOR": ["Korea", "KOR", "KR"]
    }
    
    # Find tab containers with regional codes
    tab_containers = soup.find_all('div', class_='bbCodeTabs')
    
    for tab_container in tab_containers:
        tabs = tab_container.find_all('a', class_='bbCodeTab')
        tab_contents = tab_container.find_all('li', class_='bbCodeTabContent')
        
        for i, (tab, content) in enumerate(zip(tabs, tab_contents)):
            tab_text = tab.get_text().strip()
            
            # Find which region this tab represents
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
            
            # Extract code from this tab's content
            code_block = content.find('code')
            if not code_block:
                continue
                
            code_text = code_block.get_text()
            lines = code_text.strip().split('\n')
            
            code_lines = []
            for line in lines:
                line = line.strip()
                if re.match(r'^[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8}', line):
                    hex_parts = re.findall(r'[0-9A-Fa-f]{8}', line)
                    if len(hex_parts) >= 2:
                        code_lines.append(f"{hex_parts[0]} {hex_parts[1]}")
            
            if code_lines and game_id not in results:
                results[game_id] = code_lines
    
    # If no tabs found, try to extract all code blocks
    if not results:
        code_blocks = soup.find_all('code')
        for block in code_blocks:
            code_text = block.get_text()
            lines = code_text.strip().split('\n')
            
            code_lines = []
            for line in lines:
                line = line.strip()
                if re.match(r'^[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8}', line):
                    hex_parts = re.findall(r'[0-9A-Fa-f]{8}', line)
                    if len(hex_parts) >= 2:
                        code_lines.append(f"{hex_parts[0]} {hex_parts[1]}")
            
            if code_lines:
                # Use first available region's game ID
                for region_key, game_id in regions.items():
                    if game_id and game_id not in results:
                        results[game_id] = code_lines
                        break
    
    return results


def main():
    print("=" * 60)
    print("CC Patch Collector with Game ID Mapping")
    print("=" * 60)
    
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    collected = {}
    failed = []
    total = len(GAMES)
    
    for i, (game_name, game_info) in enumerate(GAMES.items(), 1):
        post_id = game_info["post_id"]
        url = f"https://gbatemp.net/threads/new-classic-controller-hacks.659837/post-{post_id}"
        print(f"\n[{i}/{total}] {game_name}...")
        
        try:
            response = scraper.get(url, timeout=30)
            
            if response.status_code == 200:
                codes = extract_codes_by_region(response.text, game_info)
                
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
                            print(f"  - {game_id}: Empty or invalid code")
                else:
                    print(f"  - No regional codes found")
                    failed.append(game_name)
            else:
                print(f"  ✗ HTTP {response.status_code}")
                failed.append(game_name)
            
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
    print(f"\nMetadata: {metadata_path}")
    print(f"GCT files: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
