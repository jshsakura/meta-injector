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
        """
        # Check if running as PyInstaller bundle first
        if getattr(sys, 'frozen', False):
            # When packaged with PyInstaller, resources are in _MEIPASS
            meipass_path = Path(sys._MEIPASS) / "resources"
            if meipass_path.exists():
                return meipass_path
        
        # When running as a script, use the project_root from paths.py
        # This centralizes the logic for finding the project root.
        try:
            from .paths import paths
            resources_path = paths.project_root / "resources"

            if resources_path.exists():
                return resources_path
            
            # As a final fallback, create and return the directory.
            print(f"[WARN] Resources directory not found at {resources_path}. Creating it.")
            resources_path.mkdir(parents=True, exist_ok=True)
            return resources_path
        except ImportError:
            # Fallback for rare cases where paths.py is not available
            fallback_path = Path(__file__).parent.parent.parent / "resources"
            if not fallback_path.exists():
                fallback_path.mkdir(parents=True, exist_ok=True)
            return fallback_path

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
