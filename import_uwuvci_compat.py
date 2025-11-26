"""Import UWUVCI compatibility data without GameTDB (faster)."""
import sqlite3
import json
import urllib.request
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def download_compat_data(url):
    """Download compatibility JSON from GitHub."""
    print(f"Downloading compatibility data...")
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode('utf-8'))
    return data


def load_local_compat_data(json_path):
    """Load compatibility data from local JSON file."""
    print(f"Loading local compatibility data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def map_status(status_code):
    """Map UWUVCI status code to text."""
    mapping = {
        0: "Doesn't work",
        1: "Partially works",
        2: "Works"
    }
    return mapping.get(status_code, "Unknown")


def map_gamepad(gamepad_code):
    """Map UWUVCI gamepad code to text."""
    mapping = {
        0: "Doesn't work",
        1: "Partially works",
        2: "Works"
    }
    return mapping.get(gamepad_code, "Unknown")


def import_to_db(json_data, db_path, use_online=False):
    """
    Import JSON data to SQLite database.

    Args:
        json_data: Compatibility data
        db_path: Path to database
        use_online: If True, download from GitHub. If False, use local data.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get compatibility list
    compatibility_list = json_data.get('compatibility', [])
    total = len(compatibility_list)

    imported = 0
    updated = 0

    print(f"\nProcessing {total} entries...")

    for idx, entry in enumerate(compatibility_list, 1):
        game_name = entry.get('game_name', '')
        game_region = entry.get('game_region', '')
        base_name = entry.get('base_name', '')
        status_code = entry.get('status', 0)
        gamepad_code = entry.get('gamepad', 0)
        notes = entry.get('notes', '')

        # Map codes to text
        status = map_status(status_code)
        gamepad = map_gamepad(gamepad_code)

        print(f"[{idx}/{total}] {game_name} ({game_region})")

        # Check if entry already exists
        cursor.execute("""
            SELECT id FROM games
            WHERE title = ? AND region = ?
        """, (game_name, game_region))

        existing = cursor.fetchone()

        if existing:
            # Update existing entry (keep existing game_id if present)
            cursor.execute("""
                UPDATE games
                SET host_game = ?,
                    gamepad_compatibility = ?,
                    status = ?,
                    notes = ?,
                    category = 'Wii'
                WHERE title = ? AND region = ?
            """, (base_name, gamepad, status, notes, game_name, game_region))
            updated += 1
        else:
            # Insert new entry (game_id will be NULL, filled later from actual file)
            cursor.execute("""
                INSERT INTO games
                (title, region, game_id, host_game, gamepad_compatibility, status, notes, category)
                VALUES (?, ?, NULL, ?, ?, ?, ?, 'Wii')
            """, (game_name, game_region, base_name, gamepad, status, notes))
            imported += 1

        # Commit every 50 entries to avoid losing progress
        if idx % 50 == 0:
            conn.commit()

    conn.commit()
    conn.close()

    return imported, updated


def main(use_online=True):
    """
    Main import function.

    Args:
        use_online: If True, download from GitHub. If False, use local file.
    """
    try:
        if use_online:
            # Download Wii compatibility data from GitHub
            wii_url = "https://raw.githubusercontent.com/UWUVCI-PRIME/UWUVCI-Compatibility/main/WIICompat.json"
            json_data = download_compat_data(wii_url)
            print(f"Downloaded {len(json_data.get('compatibility', []))} entries from UWUVCI-PRIME")
        else:
            # Load from local resources
            json_path = Path(__file__).parent / "resources" / "compatibility" / "WIICompat.json"
            if not json_path.exists():
                print(f"[ERROR] Local file not found: {json_path}")
                return
            json_data = load_local_compat_data(json_path)
            print(f"Loaded {len(json_data.get('compatibility', []))} entries from local file")

        # Import to database
        db_path = Path(__file__).parent / "resources" / "compatibility.db"
        imported, updated = import_to_db(json_data, db_path, use_online)

        print(f"\n{'='*60}")
        print(f"[OK] Import complete!")
        print(f"  - New entries: {imported}")
        print(f"  - Updated entries: {updated}")
        print(f"  - Total processed: {imported + updated}")
        print(f"\n  Note: Game IDs will be auto-filled when you add game files")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    # Check if --online flag is provided
    use_online = '--online' in sys.argv
    main(use_online)
