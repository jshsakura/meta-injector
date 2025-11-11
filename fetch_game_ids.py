"""Fetch game IDs from GameTDB and update compatibility database."""
import requests
import xml.etree.ElementTree as ET
from src.wiivc_injector.compatibility_db import compatibility_db
from difflib import SequenceMatcher

def download_gametdb():
    """Download GameTDB XML for Wii games."""
    print("Downloading GameTDB Wii database...")
    url = "https://www.gametdb.com/wiitdb.xml?LANG=EN"
    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        print("Download complete!")
        return response.content
    else:
        print(f"Failed to download: {response.status_code}")
        return None

def parse_gametdb(xml_content):
    """Parse GameTDB XML and extract game IDs and titles."""
    print("Parsing GameTDB...")
    root = ET.fromstring(xml_content)

    games = {}
    for game in root.findall('game'):
        game_id = game.find('id')
        if game_id is not None:
            game_id_text = game_id.text

            # Get English title
            locale = game.find("locale[@lang='EN']")
            if locale is not None:
                title = locale.find('title')
                if title is not None:
                    title_text = title.text
                    games[game_id_text] = title_text

    print(f"Parsed {len(games)} games from GameTDB")
    return games

def find_best_match(game_title, gametdb_games, threshold=0.6):
    """Find best matching game ID for a title."""
    best_match = None
    best_ratio = 0

    # Clean title for comparison
    clean_title = game_title.lower().strip()

    for game_id, db_title in gametdb_games.items():
        clean_db_title = db_title.lower().strip()

        # Calculate similarity
        ratio = SequenceMatcher(None, clean_title, clean_db_title).ratio()

        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = game_id

    return best_match, best_ratio

def update_game_ids():
    """Update game IDs in compatibility database."""
    # Download GameTDB
    xml_content = download_gametdb()
    if not xml_content:
        print("Failed to download GameTDB")
        return

    # Parse GameTDB
    gametdb_games = parse_gametdb(xml_content)

    # Get all games from compatibility DB
    all_games = compatibility_db.get_all_games()

    print(f"\nMatching {len(all_games)} games...")
    matched = 0
    not_matched = 0

    for game in all_games:
        # Skip if already has game_id
        if game['game_id']:
            continue

        title = game['title']
        region = game['region']

        # Find best match
        game_id, ratio = find_best_match(title, gametdb_games)

        if game_id:
            # Verify region matches
            region_code = game_id[3] if len(game_id) >= 4 else ''
            expected_region_map = {
                'E': 'USA',
                'P': 'EUR',
                'J': 'JAP',
                'K': 'KOR'
            }
            expected_region = expected_region_map.get(region_code, 'USA')

            if expected_region == region or ratio > 0.9:  # High confidence or exact region match
                compatibility_db.update_game_id(title, region, game_id)
                print(f"✓ {title} ({region}) = {game_id} ({ratio:.2f})")
                matched += 1
            else:
                print(f"✗ {title} ({region}) - region mismatch: {game_id} ({ratio:.2f})")
                not_matched += 1
        else:
            print(f"✗ {title} ({region}) - no match found")
            not_matched += 1

    print(f"\n=== Summary ===")
    print(f"Matched: {matched}")
    print(f"Not matched: {not_matched}")
    print(f"\nDatabase updated!")

if __name__ == "__main__":
    update_game_ids()
