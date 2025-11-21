"""Resource handler for WiiVC Injector."""
import os
import sys
from pathlib import Path
from typing import Optional


class ResourceManager:
    """Manages embedded and external resources."""

    def __init__(self):
        """Initialize resource manager."""
        # Get the resources directory
        self.resources_dir = self._get_resources_dir()

    def _get_resources_dir(self) -> Path:
        """
        Get the resources directory path.

        Returns:
            Path to resources directory
        """
        # Check if running as PyInstaller bundle first
        if getattr(sys, 'frozen', False):
            # When packaged with PyInstaller
            meipass_path = Path(sys._MEIPASS) / "resources"
            if meipass_path.exists():
                return meipass_path

        # Try different possible locations for source
        possible_paths = [
            # When running from source
            Path(__file__).parent.parent.parent / "resources",
            # When installed as package
            Path(__file__).parent / "resources",
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # Default to first path and create if needed
        default_path = possible_paths[0]
        default_path.mkdir(parents=True, exist_ok=True)
        return default_path

    def get_resource_path(self, filename: str) -> Optional[Path]:
        """
        Get path to a resource file.

        Args:
            filename: Resource filename

        Returns:
            Path to resource or None if not found
        """
        resource_path = self.resources_dir / filename
        if resource_path.exists():
            return resource_path
        return None

    def get_game_database(self) -> Optional[Path]:
        """
        Get path to game database file.

        Returns:
            Path to wiitdb.txt or None
        """
        return self.get_resource_path("wiitdb.txt")

    def read_resource_bytes(self, filename: str) -> Optional[bytes]:
        """
        Read resource file as bytes.

        Args:
            filename: Resource filename

        Returns:
            Bytes content or None
        """
        resource_path = self.get_resource_path(filename)
        if resource_path:
            try:
                with open(resource_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading resource {filename}: {e}")
        return None

    def read_resource_text(self, filename: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read resource file as text.

        Args:
            filename: Resource filename
            encoding: Text encoding

        Returns:
            Text content or None
        """
        resource_path = self.get_resource_path(filename)
        if resource_path:
            try:
                with open(resource_path, 'r', encoding=encoding) as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading resource {filename}: {e}")
        return None


# Global resource manager instance
resources = ResourceManager()
