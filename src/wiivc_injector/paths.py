"""Path constants and utilities for WiiVC Injector."""
from pathlib import Path
import os
import sys


class PathManager:
    """Manages all paths used by the application."""

    def __init__(self):
        """Initialize path manager."""
        # Project root directory (handle PyInstaller frozen state)
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            self.project_root = Path(sys.executable).parent
        else:
            # Running as script
            self.project_root = Path(__file__).parent.parent.parent

        # Base temp directory
        self.temp_root = Path(os.environ.get('TEMP', '/tmp')) / "WiiVCInjector"

        # Source temp directory
        self.temp_source = self.temp_root / "SOURCETEMP"

        # Build directory
        self.temp_build = self.temp_root / "BUILDDIR"

        # Tools directory - use project folder instead of temp
        self.temp_tools = self.project_root / "core"

        # Specific source file paths
        self.temp_icon = self.temp_source / "iconTex.png"
        self.temp_banner = self.temp_source / "bootTvTex.png"
        self.temp_drc = self.temp_source / "bootDrcTex.png"
        self.temp_logo = self.temp_source / "bootLogoTex.png"
        self.temp_sound = self.temp_source / "bootSound.wav"

        # JNUSTool downloads - try multiple locations
        if os.name == 'nt':
            # Windows: CommonApplicationData
            self.jnustool_downloads = Path(os.environ.get('PROGRAMDATA', 'C:\\ProgramData')) / "JNUSToolDownloads"
        else:
            # Linux/Mac: user's home
            self.jnustool_downloads = Path.home() / ".JNUSToolDownloads"

        # Project-local base files cache (more reliable)
        self.base_files_cache = self.project_root / "base_files"

    def create_temp_directories(self):
        """Create all necessary temporary directories."""
        self.temp_root.mkdir(parents=True, exist_ok=True)
        self.temp_source.mkdir(parents=True, exist_ok=True)
        self.temp_build.mkdir(parents=True, exist_ok=True)
        self.temp_tools.mkdir(parents=True, exist_ok=True)
        self.jnustool_downloads.mkdir(parents=True, exist_ok=True)

    def cleanup_temp(self):
        """Clean up temporary directories."""
        import shutil
        if self.temp_root.exists():
            try:
                shutil.rmtree(self.temp_root)
            except Exception as e:
                print(f"Warning: Could not clean up temp directory: {e}")

    def get_tool_path(self, tool_name: str) -> Path:
        """
        Get path to a tool executable.

        Args:
            tool_name: Name of the tool (e.g., 'wit', 'chdman')

        Returns:
            Path to tool executable
        """
        if os.name == 'nt':
            tool_name = f"{tool_name}.exe"
        return self.temp_tools / tool_name


# Global path manager instance
paths = PathManager()
