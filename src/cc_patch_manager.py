"""
CC Patch Manager - Unified GCT Patch Management System

Manages GCT patches for Wii games, providing:
- Patch discovery from core/CCPatches folder
- Game ID-based patch lookup
- Unified interface for Galaxy patches and CC patches
"""

from pathlib import Path
from typing import Dict, List, Optional
import re


class CCPatchManager:
    """Manages GCT patches for Wii games."""
    
    def __init__(self, project_root: Path = None, bundle_root: Path = None):
        """
        Initialize patch manager.
        
        Args:
            project_root: Project root directory (for development)
            bundle_root: Bundle root directory (for packaged EXE)
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.bundle_root = bundle_root or self.project_root
        self._cache: Dict[str, List[dict]] = {}
        self._scanned = False
    
    @property
    def patches_dir(self) -> Path:
        """Get CCPatches directory, checking bundle first."""
        bundle_path = self.bundle_root / "core" / "CCPatches"
        if bundle_path.exists():
            return bundle_path
        return self.project_root / "core" / "CCPatches"

    @property
    def generic_patches_dir(self) -> Path:
        """Get Generic patches directory."""
        path = self.patches_dir / "Generic"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def _parse_gct_filename(self, gct_path: Path) -> Optional[dict]:
        """
        Parse GCT filename to extract game ID and patch type.

        Supported formats:
        - RMGE01-AllStars.gct -> game_id=RMGE01, patch_type=allstars
        - RMGE01-Nvidia.gct -> game_id=RMGE01, patch_type=nvidia
        - RMGE01-AllStars-RemoveDeflicker.gct -> game_id=RMGE01, patch_type=allstars_nodeflicker
        - ROUE5G.gct -> game_id=ROUE5G, patch_type=cc (Classic Controller)
        """
        filename = gct_path.stem  # Without extension

        # Pattern 1: GAMEID-Type or GAMEID-Type-Extra
        match = re.match(r'^([A-Z0-9]{4,6})-(.+)$', filename)
        if match:
            game_id = match.group(1)
            type_part = match.group(2).lower()

            # Normalize patch types
            if 'allstars' in type_part and 'deflicker' in type_part:
                patch_type = 'allstars_nodeflicker'
                display_name = 'Galaxy AllStars (No Deflicker)'
            elif 'nvidia' in type_part and 'deflicker' in type_part:
                patch_type = 'nvidia_nodeflicker'
                display_name = 'Galaxy Nvidia (No Deflicker)'
            elif 'allstars' in type_part:
                patch_type = 'allstars'
                display_name = 'Galaxy AllStars'
            elif 'nvidia' in type_part:
                patch_type = 'nvidia'
                display_name = 'Galaxy Nvidia'
            elif 'cc' in type_part:
                patch_type = 'cc'
                display_name = 'Classic Controller'
            else:
                patch_type = type_part.replace('-', '_')
                display_name = type_part.replace('-', ' ').title()

            return {
                'game_id': game_id,
                'patch_type': patch_type,
                'display_name': display_name,
                'path': gct_path,
                'filename': gct_path.name
            }

        # Pattern 2: Just GAMEID (default CC patch)
        match = re.match(r'^([A-Z0-9]{4,6})$', filename)
        if match:
            game_id = match.group(1)
            return {
                'game_id': game_id,
                'patch_type': 'cc',
                'display_name': 'Classic Controller',
                'path': gct_path,
                'filename': gct_path.name
            }

        return None

    def scan_patches(self, force: bool = False) -> Dict[str, List[dict]]:
        """
        Scan CCPatches folder and build patch cache.

        Returns:
            Dict mapping game_id to list of available patches
        """
        if self._scanned and not force:
            return self._cache

        self._cache.clear()
        patches_dir = self.patches_dir

        if not patches_dir.exists():
            print(f"[CCPatch] Patches directory not found: {patches_dir}")
            self._scanned = True
            return self._cache

        # Scan game-specific .gct files (GameID-Type.gct)
        for gct_file in patches_dir.glob("*.gct"):
            patch_info = self._parse_gct_filename(gct_file)
            if patch_info:
                game_id = patch_info['game_id']
                if game_id not in self._cache:
                    self._cache[game_id] = []
                self._cache[game_id].append(patch_info)

        # Scan Generic patches in Generic/ subdirectory
        generic_dir = self.generic_patches_dir
        if generic_dir.exists():
            if 'GENERIC' not in self._cache:
                self._cache['GENERIC'] = []
                
            for gct_file in generic_dir.glob("*.gct"):
                # Use filename as display name
                display_name = gct_file.stem.replace('_', ' ').replace('-', ' ').title()
                patch_info = {
                    'game_id': 'GENERIC',
                    'patch_type': 'generic',
                    'display_name': f"Generic: {display_name}",
                    'path': gct_file,
                    'filename': gct_file.name
                }
                self._cache['GENERIC'].append(patch_info)
        
        print(f"[CCPatch] Scanned {sum(len(v) for v in self._cache.values())} patches for {len(self._cache)} games")
        self._scanned = True
        return self._cache
        
    def get_available_patches(self, game_id: str) -> List[dict]:
        """
        Get a list of available patches for a given game ID.
        
        Args:
            game_id: The 6-character game ID (e.g., 'RMGE01').
            
        Returns:
            A list of dictionaries, each representing a patch.
        """
        self.scan_patches() # Ensure patches are scanned
        patches = []
        
        # Direct match
        if game_id in self._cache:
            patches.extend(self._cache[game_id])
        
        # Try without region suffix (e.g., RMGE01 -> RMGE)
        elif len(game_id) >= 4:
            game_id_4 = game_id[:4]
            for cached_id in self._cache:
                if cached_id.startswith(game_id_4):
                    patches.extend(self._cache[cached_id])
                    break
        
        # Always append Generic patches
        if 'GENERIC' in self._cache:
            patches.extend(self._cache['GENERIC'])
            
        return patches
    
    def get_patch_path(self, game_id: str, patch_type: str) -> Optional[Path]:
        """
        Get the path to a specific patch file.
        
        Args:
            game_id: Game ID
            patch_type: Patch type (e.g., 'allstars', 'nvidia', 'cc')
            
        Returns:
            Path to GCT file, or None if not found
        """
        patches = self.get_available_patches(game_id)
        for patch in patches:
            if patch['patch_type'] == patch_type:
                return patch['path']
        return None
    
    def has_patches(self, game_id: str) -> bool:
        """Check if any patches are available for a game."""
        return len(self.get_available_patches(game_id)) > 0


# Global singleton instance
_instance: Optional[CCPatchManager] = None


def get_cc_patch_manager(project_root: Path = None, bundle_root: Path = None) -> CCPatchManager:
    """Get or create the global CCPatchManager instance."""
    global _instance
    if _instance is None:
        _instance = CCPatchManager(project_root, bundle_root)
    return _instance
