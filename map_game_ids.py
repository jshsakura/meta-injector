"""Map game IDs from wiitdb.txt to compatibility database."""
from pathlib import Path
from difflib import SequenceMatcher
from src.wiivc_injector.compatibility_db import compatibility_db

def load_wiitdb(file_path):
    """Load game database from wiitdb.txt."""
    print(f"Loading {file_path}...")
    games = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('TITLES ='):
                continue

            parts = line.split(' = ', 1)
            if len(parts) == 2:
                game_id, game_name = parts
                games[game_id] = game_name

    print(f"Loaded {len(games)} games from wiitdb.txt")
    return games

def find_best_match(game_title, wiitdb_games, region, threshold=0.7):
    """Find best matching game ID for a title."""
    best_match = None
    best_ratio = 0

    # Clean title for comparison
    clean_title = game_title.lower().strip()

    # Region code mapping
    region_code_map = {
        'USA': 'E',
        'EUR': 'P',
        'JAP': 'J',
        'KOR': 'K'
    }
    expected_region_code = region_code_map.get(region, 'E')

    for game_id, db_title in wiitdb_games.items():
        # Check region match
        if len(game_id) >= 4:
            game_region_code = game_id[3]
            if game_region_code != expected_region_code:
                continue  # Skip wrong region

        clean_db_title = db_title.lower().strip()

        # Calculate similarity
        ratio = SequenceMatcher(None, clean_title, clean_db_title).ratio()

        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = game_id

    return best_match, best_ratio

def update_game_ids():
    """Update game IDs in compatibility database."""
    # Load wiitdb.txt
    wiitdb_path = Path(__file__).parent / "resources" / "wiitdb.txt"
    if not wiitdb_path.exists():
        print(f"Error: {wiitdb_path} not found!")
        return

    wiitdb_games = load_wiitdb(wiitdb_path)

    # Get all games from compatibility DB
    all_games = compatibility_db.get_all_games()

    print(f"\nMatching {len(all_games)} games...")
    matched = 0
    not_matched = 0

    for game in all_games:
        # Skip if already has game_id
        if game['game_id']:
            matched += 1
            continue

        title = game['title']
        region = game['region']

        # Find best match
        game_id, ratio = find_best_match(title, wiitdb_games, region)

        if game_id and ratio >= 0.7:
            compatibility_db.update_game_id(title, region, game_id)
            print(f"OK {title} ({region}) = {game_id} ({ratio:.2f})")
            matched += 1
        else:
            if game_id:
                print(f"LOW {title} ({region}) = {game_id} ({ratio:.2f}) - skipped")
            else:
                print(f"NONE {title} ({region})")
            not_matched += 1

    print(f"\n=== Summary ===")
    print(f"Matched: {matched}")
    print(f"Not matched: {not_matched}")
    print(f"Total: {len(all_games)}")
    print(f"\nDatabase updated!")

if __name__ == "__main__":
    update_game_ids()
