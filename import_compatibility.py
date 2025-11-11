"""Import compatibility.csv to database."""
from pathlib import Path
from src.wiivc_injector.compatibility_db import compatibility_db

# Import CSV
csv_path = Path(__file__).parent / "compatibility.csv"
print(f"Importing from {csv_path}...")

compatibility_db.import_from_csv(csv_path)

# Show stats
stats = compatibility_db.get_stats()
print(f"\n=== Database Statistics ===")
print(f"Total games: {stats['total_games']}")
print(f"Games with title keys: {stats['games_with_keys']}")
print(f"Total host games: {stats['total_hosts']}")

print(f"\n=== Host Games ===")
for host in compatibility_db.get_host_games():
    print(f"  - {host}")

print(f"\nDatabase saved to: {compatibility_db.db_path}")
print("Done!")
