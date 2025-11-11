"""Setup default title keys for host games."""
from src.wiivc_injector.compatibility_db import compatibility_db

# Set title keys for host games
print("Setting up default title keys...")

# Rhythm Heaven Fever (USA)
rhf_key = "04eacef7657422e61606fa7fc7dcd73d"
compatibility_db.set_host_game_title_key("Rhythm Heaven Fever (USA)", rhf_key)
print(f"OK Rhythm Heaven Fever (USA): {rhf_key}")

# Xenoblade Chronicles (USA)
xbc_key = "0fdfd8608ed4ed45ab0d4fda1071c6cc"
compatibility_db.set_host_game_title_key("Xenoblade Chronicles (USA)", xbc_key)
print(f"OK Xenoblade Chronicles (USA): {xbc_key}")

# Super Mario Galaxy 2 (EUR) - use Rhythm Heaven Fever as default
compatibility_db.set_host_game_title_key("Super Mario Galaxy 2 (EUR)", rhf_key)
print(f"OK Super Mario Galaxy 2 (EUR): {rhf_key} (default)")

print("\nDone! Title keys have been saved to the database.")
print(f"Database location: {compatibility_db.db_path}")
