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
            # Use _MEIPASS for bundled resources (core, resources)
            self.bundle_root = Path(sys._MEIPASS)
            # Use exe directory for user data (output, cache, etc)
            self.project_root = Path(sys.executable).parent
        else:
            # Running as script (src/paths.py -> src/ -> project_root/)
            self.project_root = Path(__file__).parent.parent
            self.bundle_root = self.project_root

        # Core directory (tools and patches)
        self.core = self.bundle_root / "core"

        # Base temp directory (system temp - TeconMoon/UWUVCI style)
        self.temp_root = Path(os.environ.get('TEMP', '/tmp')) / "MetaInjector"

        # Source temp directory (빌드마다 삭제)
        self.temp_source = self.temp_root / "SOURCETEMP"

        # Build directory (빌드마다 삭제)
        self.temp_build = self.temp_root / "BUILDDIR"

        # Tools directory (빌드마다 삭제)
        self.temp_tools = self.temp_root / "TOOLDIR"

        # Cache directories (빌드 시 삭제하지 않음 - 영구 캐시)
        self.images_cache = self.temp_root / "IMAGECACHE"
        self.base_cache = self.temp_root / "BASECACHE"

        # Specific source file paths
        self.temp_icon = self.temp_source / "iconTex.png"
        self.temp_banner = self.temp_source / "bootTvTex.png"
        self.temp_drc = self.temp_source / "bootDrcTex.png"
        self.temp_logo = self.temp_source / "bootLogoTex.png"
        self.temp_sound = self.temp_source / "bootSound.wav"

        # Build log file (cleared before each build)
        self.build_log = self.temp_root / "build_log.txt"

        # Legacy compatibility (일부 코드에서 사용할 수 있음)
        self.jnustool_downloads = self.base_cache

    def create_temp_directories(self):
        """Create all necessary temporary directories."""
        self.temp_root.mkdir(parents=True, exist_ok=True)
        self.temp_source.mkdir(parents=True, exist_ok=True)
        self.temp_build.mkdir(parents=True, exist_ok=True)
        self.temp_tools.mkdir(parents=True, exist_ok=True)
        # JNUSToolDownloads는 CommonApplicationData에 있으므로 여기서 생성 안함

    def cleanup_temp(self):
        """Clean up temporary directories."""
        import shutil
        if self.temp_root.exists():
            try:
                shutil.rmtree(self.temp_root)
            except Exception as e:
                print(f"Warning: Could not clean up temp directory: {e}")

    def clear_build_log(self):
        """Clear build log file (called at start of each build)."""
        try:
            self.temp_root.mkdir(parents=True, exist_ok=True)
            with open(self.build_log, 'w', encoding='utf-8') as f:
                from datetime import datetime
                f.write(f"=== Build Log Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
        except Exception as e:
            print(f"Warning: Could not clear build log: {e}")

    def append_build_log(self, message: str):
        """Append message to build log file."""
        try:
            with open(self.build_log, 'a', encoding='utf-8') as f:
                f.write(message + "\n")
        except Exception as e:
            print(f"Warning: Could not write to build log: {e}")

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
