"""Game information extraction utilities."""
import struct
from pathlib import Path
from typing import Optional, Dict


class GameInfoExtractor:
    """Extract information from game ISO/WBFS files."""

    @staticmethod
    def read_game_header(iso_path: Path) -> Optional[Dict[str, str]]:
        """
        Read game header information from ISO.

        Supports:
        - Standard ISO/GCM
        - WBFS format
        - NASOS format (WII5, WII9)
        - NKIT format

        Args:
            iso_path: Path to ISO/WBFS file

        Returns:
            Dict with game_id and title, or None
        """
        try:
            with open(iso_path, 'rb') as f:
                # Read first few bytes to detect format
                header_check = f.read(4)
                f.seek(0)

                offset = 0
                is_wbfs = False
                is_nasos = False

                # Check for WBFS format
                if header_check == b'WBFS':
                    is_wbfs = True
                    offset = 0x200  # WBFS header offset
                    print("Detected WBFS format")

                # Check for NASOS format
                elif header_check == b'WII5':
                    is_nasos = True
                    offset = 0x1182800
                    print("Detected NASOS (WII5) format")

                elif header_check == b'WII9':
                    is_nasos = True
                    offset = 0x1FB5000
                    print("Detected NASOS (WII9) format")

                # Check for NKIT format (at 0x200)
                else:
                    f.seek(0x200)
                    nkit_check = f.read(4)
                    if nkit_check == b'NKIT':
                        print("Detected NKIT format")
                    f.seek(0)

                # Read from correct offset
                f.seek(offset)
                header = f.read(0x60)

                if len(header) < 0x60:
                    print(f"Header too short: {len(header)} bytes")
                    return None

                # Game ID (6 bytes at offset+0x00)
                game_id_bytes = header[0:6]

                # Try to decode as ASCII
                try:
                    game_id = game_id_bytes.decode('ascii').strip()
                    # Validate - should be alphanumeric
                    if not game_id or not game_id[0].isalpha():
                        print(f"Invalid game ID: {game_id_bytes.hex()}")
                        return None
                except:
                    print(f"Failed to decode game ID: {game_id_bytes.hex()}")
                    return None

                # Game title (starts at offset+0x20, null-terminated)
                title_bytes = header[0x20:0x60]
                # Find null terminator
                null_pos = title_bytes.find(b'\x00')
                if null_pos != -1:
                    title_bytes = title_bytes[:null_pos]

                try:
                    game_title = title_bytes.decode('ascii', errors='ignore').strip()
                except:
                    game_title = "Unknown"

                # Read game type (8 bytes at offset+0x18)
                f.seek(offset + 0x18)
                game_type_bytes = f.read(8)
                game_type = int.from_bytes(game_type_bytes, byteorder='big', signed=False)

                print(f"Extracted: ID={game_id}, Title={game_title}, Type={game_type}")

                return {
                    'game_id': game_id,
                    'title': game_title if game_title else "Unknown",
                    'system': GameInfoExtractor._detect_system(game_id),
                    'is_wbfs': is_wbfs,
                    'is_nasos': is_nasos,
                    'game_type': game_type
                }

        except Exception as e:
            print(f"Error reading game header: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def _detect_system(game_id: str) -> str:
        """
        Detect system type from game ID.

        Args:
            game_id: 6-character game ID

        Returns:
            System type: 'wii', 'gc', or 'unknown'
        """
        if not game_id or len(game_id) < 1:
            return 'unknown'

        # First character indicates system
        first_char = game_id[0].upper()

        if first_char == 'R' or first_char == 'S':
            # R = Wii, S = Wii (some titles)
            return 'wii'
        elif first_char == 'G':
            # G = GameCube
            return 'gc'
        else:
            return 'unknown'

    @staticmethod
    def detect_file_type(file_path: Path) -> str:
        """
        Detect file type (ISO, WBFS, NKIT, NASOS).

        Args:
            file_path: Path to file

        Returns:
            File type string
        """
        filename = file_path.name.lower()

        if filename.endswith('.nkit.iso'):
            return 'nkit'
        elif filename.endswith('.iso.dec'):
            return 'nasos'
        elif filename.endswith('.wbfs'):
            return 'wbfs'
        elif filename.endswith('.iso'):
            return 'iso'
        elif filename.endswith('.gcm'):
            return 'gcm'
        else:
            return 'unknown'

    @staticmethod
    def generate_title_id(game_id: str) -> str:
        """
        Generate Title ID from Game ID.

        For Wii VC Inject: Use 00050002 prefix (Homebrew/Custom content area)
        This avoids conflicts with official Nintendo titles (00050000)

        Args:
            game_id: 6-character game ID

        Returns:
            16-character hex Title ID
        """
        if not game_id or len(game_id) < 4:
            return "0005000200000000"

        # Format: 00050002 + Game ID (4 chars ASCII hex)
        # Example: RUUK → 00050002 + 5255554B = 000500025255554B
        game_id_hex = game_id[:4].encode('ascii').hex().upper()
        title_id = "00050002" + game_id_hex

        return title_id

    @staticmethod
    def extract_game_info(file_path: Path) -> Optional[Dict[str, str]]:
        """
        Extract complete game information.

        Args:
            file_path: Path to game file

        Returns:
            Dict with all game info
        """
        if not file_path.exists():
            return None

        info = GameInfoExtractor.read_game_header(file_path)
        if not info:
            return None

        file_type = GameInfoExtractor.detect_file_type(file_path)
        title_id = GameInfoExtractor.generate_title_id(info['game_id'])

        info.update({
            'file_type': file_type,
            'title_id': title_id,
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size
        })

        # Fetch localized names and update compatibility DB
        game_id = info.get('game_id', '')
        if game_id and len(game_id) >= 4:
            try:
                from .game_tdb import GameTdb
                from .compatibility_db import compatibility_db

                # Get localized names from GameTDB
                names = GameTdb.get_localized_names(game_id)
                korean_title = names.get('local_name')
                english_title = names.get('english_name')

                # Store in info for display
                if korean_title:
                    info['korean_title'] = korean_title
                if english_title:
                    info['english_title'] = english_title

                # Update compatibility DB if we have any title info
                if korean_title or english_title:
                    compatibility_db.update_titles(game_id, korean_title, english_title)

            except Exception as e:
                print(f"[GameInfo] Error fetching localized names: {e}")

        return info


# Convenience instance
game_info_extractor = GameInfoExtractor()
