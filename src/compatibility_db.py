"""Compatibility database manager for WiiVC Injector."""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional


class CompatibilityDB:
    """Manages game compatibility database with title keys."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database."""
        if db_path is None:
            # Try resources directory first
            try:
                from .resources import resources
                resource_db = resources.get_resource_path("compatibility.db")
                if resource_db and resource_db.exists():
                    db_path = resource_db
                    print(f"[DB] Using database: {db_path}")
                else:
                    # Fallback to user's home directory
                    db_path = Path.home() / ".meta_injector_compatibility.db"
                    print(f"[DB] Using user database: {db_path}")
            except Exception as e:
                # Fallback to user's home directory
                db_path = Path.home() / ".meta_injector_compatibility.db"
                print(f"[DB] Using user database: {db_path}")

        self.db_path = db_path
        self.conn = None
        self.create_tables()

    def connect(self):
        """Connect to database."""
        if self.conn is None:
            # Allow SQLite to be used across threads
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_tables(self):
        """Create database tables if they don't exist."""
        conn = self.connect()
        cursor = conn.cursor()

        # Games table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                region TEXT NOT NULL,
                game_id TEXT,
                host_game TEXT NOT NULL,
                gamepad_compatibility TEXT,
                status TEXT,
                notes TEXT,
                title_key TEXT,
                user_notes TEXT,
                category TEXT DEFAULT 'Wii',
                UNIQUE(title, region)
            )
        """)

        # Migrate: Add game_id column if it doesn't exist
        try:
            cursor.execute("SELECT game_id FROM games LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            cursor.execute("ALTER TABLE games ADD COLUMN game_id TEXT")
            print("Migrated database: added game_id column")

        # Migrate: Add category column if it doesn't exist
        try:
            cursor.execute("SELECT category FROM games LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            cursor.execute("ALTER TABLE games ADD COLUMN category TEXT DEFAULT 'Wii'")
            cursor.execute("UPDATE games SET category = 'Wii' WHERE category IS NULL")
            print("Migrated database: added category column")

        # Host games table (for quick reference)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS host_games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                default_title_key TEXT
            )
        """)

        conn.commit()

    def import_from_csv(self, csv_path: Path):
        """Import compatibility data from CSV file."""
        conn = self.connect()
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute("DELETE FROM games")

        # Read CSV
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT OR REPLACE INTO games
                    (title, region, game_id, host_game, gamepad_compatibility, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['Title'],
                    row['Region'],
                    None,  # game_id will be filled later
                    row['Host_Game'],
                    row['Gamepad_Compatibility'],
                    row['Status'],
                    row['Notes']
                ))

        # Extract unique host games
        cursor.execute("SELECT DISTINCT host_game FROM games")
        host_games = cursor.fetchall()
        for host in host_games:
            cursor.execute("""
                INSERT OR IGNORE INTO host_games (name) VALUES (?)
            """, (host[0],))

        conn.commit()
        print(f"Imported {cursor.rowcount} games from {csv_path}")

    def search_games(self, query: str, region: Optional[str] = None) -> List[Dict]:
        """
        Search games by title.

        Args:
            query: Search query (title)
            region: Filter by region (optional)

        Returns:
            List of matching games
        """
        conn = self.connect()
        cursor = conn.cursor()

        sql = """
            SELECT * FROM games
            WHERE title LIKE ?
        """
        params = [f"%{query}%"]

        if region:
            sql += " AND region = ?"
            params.append(region)

        sql += " ORDER BY title, region"

        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_game(self, title: str, region: str) -> Optional[Dict]:
        """Get specific game by title and region."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM games
            WHERE title = ? AND region = ?
        """, (title, region))

        row = cursor.fetchone()
        return dict(row) if row else None

    def get_game_by_id(self, game_id: str) -> Optional[Dict]:
        """Get specific game by game ID (title ID)."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM games
            WHERE game_id = ?
            LIMIT 1
        """, (game_id,))

        row = cursor.fetchone()
        return dict(row) if row else None

    def update_game_id(self, title: str, region: str, game_id: str):
        """Update game_id for a game (learning system)."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE games
            SET game_id = ?
            WHERE title = ? AND region = ?
        """, (game_id, title, region))

        conn.commit()
        print(f"Learned game ID mapping: {title} ({region}) = {game_id}")

    def update_title(self, old_title: str, region: str, new_title: str):
        """Update title for a game."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE games
            SET title = ?
            WHERE title = ? AND region = ?
        """, (new_title, old_title, region))

        conn.commit()
        print(f"Updated title: {old_title} ({region}) -> {new_title}")

    def update_title_key(self, title: str, region: str, title_key: str):
        """Update title key for a game."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE games
            SET title_key = ?
            WHERE title = ? AND region = ?
        """, (title_key, title, region))

        conn.commit()

    def update_user_notes(self, title: str, region: str, notes: str):
        """Update user notes for a game."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE games
            SET user_notes = ?
            WHERE title = ? AND region = ?
        """, (notes, title, region))

        conn.commit()

    def get_all_games(self) -> List[Dict]:
        """Get all games."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM games ORDER BY title, region")
        return [dict(row) for row in cursor.fetchall()]

    def fill_missing_game_ids(self):
        """Fill missing game IDs by searching GameTDB with game titles."""
        from .game_tdb import GameTdb
        import re

        conn = self.connect()
        cursor = conn.cursor()

        # Get games with missing game_id
        cursor.execute("SELECT title, region FROM games WHERE game_id IS NULL OR game_id = ''")
        missing_games = cursor.fetchall()

        updated_count = 0
        for title, region in missing_games:
            # Extract English title from parentheses if present
            # e.g., "한글제목 (English Title)" -> "English Title"
            eng_match = re.search(r'\(([^)]+)\)\s*$', title)
            search_title = eng_match.group(1) if eng_match else title

            # Search GameTDB by title
            results = GameTdb.search_by_name(search_title)

            # If no results with English title, try original title
            if not results and eng_match:
                results = GameTdb.search_by_name(title)

            if results:
                # Try to find matching region
                region_code = {'USA': 'E', 'EUR': 'P', 'JPN': 'J', 'KOR': 'K'}.get(region, '')

                best_match = None
                for game_id, game_name in results:
                    # Exact title match preferred
                    if game_name.lower() == title.lower():
                        if region_code and len(game_id) > 3 and game_id[3] == region_code:
                            best_match = game_id
                            break
                        elif not best_match:
                            best_match = game_id

                # If no exact match, use first partial match
                if not best_match and results:
                    for game_id, game_name in results:
                        if region_code and len(game_id) > 3 and game_id[3] == region_code:
                            best_match = game_id
                            break
                    if not best_match:
                        best_match = results[0][0]

                if best_match:
                    self.update_game_id(title, region, best_match)
                    updated_count += 1
                    print(f"  [DB] Found game ID for '{title}' ({region}): {best_match}")

        return updated_count

    def get_games_by_host(self, host_game: str) -> List[Dict]:
        """Get games by host game."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM games
            WHERE host_game = ?
            ORDER BY title, region
        """, (host_game,))

        return [dict(row) for row in cursor.fetchall()]

    def get_host_games(self) -> List[str]:
        """Get list of all host games."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT name FROM host_games ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

    def set_host_game_title_key(self, host_game_name: str, title_key: str):
        """Set default title key for a host game."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO host_games (name, default_title_key)
            VALUES (?, ?)
        """, (host_game_name, title_key))

        conn.commit()

    def get_host_game_title_key(self, host_game_name: str) -> Optional[str]:
        """Get default title key for a host game."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT default_title_key FROM host_games
            WHERE name = ?
        """, (host_game_name,))

        row = cursor.fetchone()
        return row[0] if row and row[0] else None

    def get_stats(self) -> Dict:
        """Get database statistics."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM games")
        total_games = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM games WHERE title_key IS NOT NULL AND title_key != ''")
        games_with_keys = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT host_game) FROM games")
        total_hosts = cursor.fetchone()[0]

        return {
            'total_games': total_games,
            'games_with_keys': games_with_keys,
            'total_hosts': total_hosts
        }

    def _auto_import_csv(self):
        """Auto-import CSV if database is empty."""
        conn = self.connect()
        cursor = conn.cursor()

        # Check if database has any games
        cursor.execute("SELECT COUNT(*) FROM games")
        count = cursor.fetchone()[0]

        if count == 0:
            # Database is empty, try to import CSV
            try:
                from .resources import resources
                csv_path = resources.get_resource_path("compatibility.csv")
                if csv_path and csv_path.exists():
                    print(f"[DB] Database empty, importing from {csv_path}")
                    self.import_from_csv(csv_path)
                else:
                    print("[DB] Warning: compatibility.csv not found in resources")
            except Exception as e:
                print(f"[DB] Error auto-importing CSV: {e}")


# Global instance
compatibility_db = CompatibilityDB()
