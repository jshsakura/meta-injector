"""WiiU VC Wii Injection Compatibility Database."""

# Compatibility status
STATUS_PERFECT = "perfect"      # Works perfectly
STATUS_PLAYABLE = "playable"    # Minor issues but playable
STATUS_ISSUES = "issues"        # Major issues
STATUS_BROKEN = "broken"        # Does not work

# Database structure:
# game_id: {
#     'title': str,
#     'region': str (NTSC-U, PAL, NTSC-J, etc.),
#     'status': str (perfect, playable, issues, broken),
#     'notes': str,
#     'recommended_settings': {
#         'force_cc': bool,
#         'video_mode': str (None, PAL50, PAL60, NTSC, etc.),
#         'video_width': int or None,
#         'c2w_patch': bool,
#     }
# }

COMPATIBILITY_DB = {
    # Example entries - to be populated with actual data
    "RMCE01": {
        "title": "Mario Kart Wii",
        "region": "NTSC-U",
        "status": STATUS_PERFECT,
        "notes": "Works perfectly with Force CC",
        "recommended_settings": {
            "force_cc": True,
            "video_mode": None,
            "video_width": None,
            "c2w_patch": False,
        }
    },
    "RSBE01": {
        "title": "Super Smash Bros. Brawl",
        "region": "NTSC-U",
        "status": STATUS_PLAYABLE,
        "notes": "Minor audio issues in some stages",
        "recommended_settings": {
            "force_cc": True,
            "video_mode": None,
            "video_width": None,
            "c2w_patch": False,
        }
    },
    "RGMJ01": {
        "title": "Super Mario Galaxy",
        "region": "NTSC-J",
        "status": STATUS_ISSUES,
        "notes": "Wiimote pointer issues, better to use actual Wii Remote",
        "recommended_settings": {
            "force_cc": False,
            "video_mode": None,
            "video_width": None,
            "c2w_patch": False,
        }
    },

    # GameCube games
    "GALE01": {
        "title": "Super Smash Bros. Melee",
        "region": "NTSC-U",
        "status": STATUS_PERFECT,
        "notes": "Works perfectly",
        "recommended_settings": {
            "force_cc": True,
            "video_mode": None,
            "video_width": 640,
            "c2w_patch": True,
        }
    },
    "GM4E01": {
        "title": "Metroid Prime",
        "region": "NTSC-U",
        "status": STATUS_PERFECT,
        "notes": "Works perfectly",
        "recommended_settings": {
            "force_cc": True,
            "video_mode": None,
            "video_width": None,
            "c2w_patch": True,
        }
    },
}


def get_compatibility_info(game_id: str) -> dict:
    """
    Get compatibility information for a game.

    Args:
        game_id: 6-character game ID (e.g., "RMCE01")

    Returns:
        Dict with compatibility info, or None if not found
    """
    # Try exact match first
    if game_id in COMPATIBILITY_DB:
        return COMPATIBILITY_DB[game_id]

    # Try matching first 4 characters (game code without region)
    game_code = game_id[:4]
    for db_id, info in COMPATIBILITY_DB.items():
        if db_id[:4] == game_code:
            return info

    return None


def get_recommended_settings(game_id: str) -> dict:
    """
    Get recommended settings for a game.

    Args:
        game_id: 6-character game ID

    Returns:
        Dict with recommended settings, or default settings if not found
    """
    info = get_compatibility_info(game_id)

    if info and 'recommended_settings' in info:
        return info['recommended_settings']

    # Default settings for unknown games
    return {
        "force_cc": True,
        "video_mode": None,
        "video_width": None,
        "c2w_patch": False,
    }


def get_compatibility_status(game_id: str) -> str:
    """
    Get compatibility status for a game.

    Args:
        game_id: 6-character game ID

    Returns:
        Status string (perfect, playable, issues, broken, unknown)
    """
    info = get_compatibility_info(game_id)

    if info:
        return info.get('status', 'unknown')

    return 'unknown'


def get_compatibility_notes(game_id: str) -> str:
    """
    Get compatibility notes for a game.

    Args:
        game_id: 6-character game ID

    Returns:
        Notes string, or empty string if not found
    """
    info = get_compatibility_info(game_id)

    if info:
        return info.get('notes', '')

    return ''


def add_game_to_db(game_id: str, title: str, region: str, status: str,
                   notes: str = "", recommended_settings: dict = None):
    """
    Add a game to the compatibility database.

    Args:
        game_id: 6-character game ID
        title: Game title
        region: Region code
        status: Compatibility status
        notes: Optional notes
        recommended_settings: Optional recommended settings dict
    """
    if recommended_settings is None:
        recommended_settings = {
            "force_cc": True,
            "video_mode": None,
            "video_width": None,
            "c2w_patch": False,
        }

    COMPATIBILITY_DB[game_id] = {
        "title": title,
        "region": region,
        "status": status,
        "notes": notes,
        "recommended_settings": recommended_settings,
    }


def export_db_to_txt(output_path: str):
    """
    Export compatibility database to text file.

    Args:
        output_path: Path to output text file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WiiU VC Wii/GC Injection Compatibility Database\n")
        f.write("=" * 70 + "\n\n")

        for game_id, info in sorted(COMPATIBILITY_DB.items()):
            f.write(f"Game ID: {game_id}\n")
            f.write(f"Title: {info['title']}\n")
            f.write(f"Region: {info['region']}\n")
            f.write(f"Status: {info['status'].upper()}\n")
            f.write(f"Notes: {info['notes']}\n")
            f.write(f"\nRecommended Settings:\n")

            settings = info.get('recommended_settings', {})
            f.write(f"  - Force Classic Controller: {settings.get('force_cc', 'N/A')}\n")
            f.write(f"  - Video Mode: {settings.get('video_mode', 'Auto')}\n")
            f.write(f"  - Video Width: {settings.get('video_width', 'Auto')}\n")
            f.write(f"  - C2W Patch: {settings.get('c2w_patch', False)}\n")
            f.write("\n" + "-" * 70 + "\n\n")


def import_from_wiki_text(wiki_text: str):
    """
    Parse wiki text and add games to database.

    This function should be customized based on the actual wiki format.

    Args:
        wiki_text: Raw text copied from wiki
    """
    # TODO: Implement parsing based on actual wiki format
    pass


if __name__ == "__main__":
    # Export current database to text file
    export_db_to_txt("compatibility_list.txt")
    print("Exported compatibility database to compatibility_list.txt")
