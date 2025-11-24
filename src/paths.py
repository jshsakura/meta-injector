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
            # Running as script (src/paths.py -> src/ -> project_root/)
            self.project_root = Path(__file__).parent.parent

        # Base temp directory (system temp - TeconMoon/UWUVCI style)
        self.temp_root = Path(os.environ.get('TEMP', '/tmp')) / "WiiUVCInjector"

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
