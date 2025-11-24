"""Game database utilities for WiiVC Injector."""
import os
from typing import List, Optional, Iterator
from .string_util import replace_at


class GameTdb:
    """Game database handler for Wii game titles."""

    _RESOURCE_FILE = "wiitdb.txt"
    _cache = None

    @classmethod
    def _load_database(cls) -> dict:
        """Load the game database from resource file."""
        if cls._cache is not None:
            return cls._cache

        cls._cache = {}

        # Get the resource file path
        # In the packaged version, this will be in the resources directory
        resource_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'resources',
            cls._RESOURCE_FILE
        )

        if not os.path.exists(resource_path):
            # Try alternative path for development
            resource_path = os.path.join(
                os.path.dirname(__file__),
                'resources',
                cls._RESOURCE_FILE
            )

        try:
            with open(resource_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('TITLES ='):
                        continue

                    parts = line.split(' = ', 1)
                    if len(parts) == 2:
                        game_id, game_name = parts
                        cls._cache[game_id] = game_name
        except FileNotFoundError:
            print(f"Warning: Game database file not found at {resource_path}")

        return cls._cache

    @classmethod
    def get_name(cls, game_id: str) -> Optional[str]:
        """
        Get game name by ID.

        Args:
            game_id: Game ID to lookup

        Returns:
            Game name or None if not found
        """
        db = cls._load_database()
        return db.get(game_id)

    @classmethod
    def get_ids(cls, name: str) -> List[str]:
        """
        Get all game IDs matching a specific name.

        Args:
            name: Game name to search for

        Returns:
            List of matching game IDs
        """
        db = cls._load_database()
        return [game_id for game_id, game_name in db.items() if game_name == name]

    @classmethod
    def get_ids_starting_with(cls, id_start: str) -> List[str]:
        """
        Get all game IDs starting with a specific prefix.

        Args:
            id_start: ID prefix to search for

        Returns:
            List of matching game IDs
        """
        db = cls._load_database()
        result = []

        for game_id in sorted(db.keys()):
            if game_id.startswith(id_start):
                result.append(game_id)
            # Since IDs are sorted, we can stop early
            elif game_id[:len(id_start)] > id_start:
                break

        return result

    @classmethod
    def search_by_name(cls, search_name: str) -> List[tuple]:
        """
        Search for games by partial name match.

        Args:
            search_name: Name to search for (case-insensitive)

        Returns:
            List of (game_id, game_name) tuples
        """
        db = cls._load_database()
        search_lower = search_name.lower()
        results = []

        for game_id, game_name in db.items():
            if search_lower in game_name.lower():
                results.append((game_id, game_name))

        return results

    @classmethod
    def get_alternative_ids(cls, initial_id: str) -> Iterator[str]:
        """
        Get alternative game IDs for region variants.

        Args:
            initial_id: Initial game ID

        Yields:
            Alternative game IDs
        """
        tried = {initial_id}

        # Try common region codes
        if len(initial_id) > 3:
            # Try European version
            eur_id = replace_at(initial_id, 3, 'E')
            tried.add(eur_id)

            # Try American version
            usa_id = replace_at(initial_id, 3, 'P')
            tried.add(usa_id)

        # Yield the tried IDs first
        for game_id in tried:
            yield game_id

        # Get game name and find other IDs with same name
        game_name = cls.get_name(initial_id)
        if game_name:
            matching_ids = cls.get_ids(game_name)
            for game_id in matching_ids:
                if game_id not in tried:
                    yield game_id
                    tried.add(game_id)

        # As last resort, try matching first 3 characters
        if len(initial_id) >= 3:
            prefix_ids = cls.get_ids_starting_with(initial_id[:3])
            for game_id in prefix_ids:
                if game_id not in tried:
                    yield game_id
