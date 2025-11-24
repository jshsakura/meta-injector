"""Batch build window - Simplified UI for mass injection."""
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QLabel, QCheckBox, QFileDialog, QMessageBox, QLineEdit, QDialog,
    QFormLayout, QStyle, QProgressDialog, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QPixmap, QIcon, QFont
from .batch_builder import BatchBuilder, BatchBuildJob
from .game_info import game_info_extractor
from .compatibility_db import compatibility_db
from .paths import paths
from .translations import tr


def show_message(parent, msg_type, title, text, min_width=550):
    """Show message box without help button and with minimum width."""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setMinimumWidth(min_width)
    msg_box.setWindowFlags(msg_box.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    if msg_type == "info":
        msg_box.setIcon(QMessageBox.Information)
    elif msg_type == "warning":
        msg_box.setIcon(QMessageBox.Warning)
    elif msg_type == "question":
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg_box.exec_()

    msg_box.exec_()


class GameLoaderThread(QThread):
    """Background thread for loading game files with parallel downloads."""

    # Signals
    game_loaded = pyqtSignal(object)  # Emits BatchBuildJob when ready
    loading_finished = pyqtSignal(int)  # Total games loaded
    progress_updated = pyqtSignal(int, int)  # current, total

    def __init__(self, file_paths, auto_download_icons=True):
        super().__init__()
        self.file_paths = file_paths
        self.auto_download_icons = auto_download_icons
        self.should_stop = False

    def stop(self):
        """Stop loading games."""
        self.should_stop = True

    def run(self):
        """Load games in background with parallel downloads."""
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed

            loaded_count = 0
            total = len(self.file_paths)

            # First pass: Extract game info (fast, sequential)
            jobs_to_process = []
            for idx, file_path in enumerate(self.file_paths):
                if self.should_stop:
                    break

                try:
                    game_path = Path(file_path)
                    game_info = game_info_extractor.extract_game_info(game_path)

                    if not game_info:
                        print(f"[WARN] Failed to extract info from {game_path.name}")
                        continue

                    job = BatchBuildJob(game_path, game_info)
                    self.prepare_job_metadata(job)
                    jobs_to_process.append((idx, job))

                except Exception as e:
                    print(f"[ERROR] Failed to load {file_path}: {e}")
                    import traceback
                    traceback.print_exc()

            # Second pass: Download icons sequentially (one at a time)
            if self.auto_download_icons and jobs_to_process:
                for idx, job in jobs_to_process:
                    if self.should_stop:
                        break

                    # Download icon for this job
                    try:
                        self.download_icon_for_job(job)
                    except Exception as e:
                        print(f"[ERROR] Download failed for {job.game_path.name}: {e}")

                    # Emit job after download completes
                    self.progress_updated.emit(idx + 1, len(jobs_to_process))
                    self.game_loaded.emit(job)
                    loaded_count += 1
            else:
                # No icon download, just emit jobs
                for idx, job in jobs_to_process:
                    if self.should_stop:
                        break
                    self.progress_updated.emit(idx + 1, total)
                    self.game_loaded.emit(job)
                    loaded_count += 1

            self.loading_finished.emit(loaded_count)

        except Exception as e:
            print(f"[CRITICAL ERROR] GameLoaderThread crashed: {e}")
            import traceback
            traceback.print_exc()
            # Emit finished signal even on error to prevent UI freeze
            self.loading_finished.emit(0)

    def prepare_job_metadata(self, job: BatchBuildJob):
        """Prepare job metadata from game info and DB."""
        game_info = job.game_info
        game_id = game_info.get('game_id', '')
        game_title = game_info.get('title', '')

        # Get region
        region_map = {'P': 'EUR', 'E': 'USA', 'J': 'JAP', 'K': 'KOR'}
        region_code = game_id[3] if len(game_id) >= 4 else 'E'
        region = region_map.get(region_code, 'USA')

        # Search in compatibility DB
        found_game = None
        if game_id:
            found_game = compatibility_db.get_game_by_id(game_id)

        if not found_game and game_title:
            games = compatibility_db.search_games(game_title, region)
            if games:
                found_game = games[0]

        # Set title name - will be updated from GameTDB later if available
        # For now, use DB title or game_info title as fallback
        if found_game and found_game['title']:
            db_title = found_game['title'].split('(')[0].strip()
            job.title_name = db_title
            job.db_title = db_title  # Save for fallback
        else:
            job.title_name = game_title
            job.db_title = game_title

        # Get gamepad compatibility and host game from DB
        if found_game:
            job.gamepad_compatibility = found_game.get('gamepad_compatibility', 'Unknown')
            job.host_game = found_game.get('host_game', '')
        else:
            job.gamepad_compatibility = 'Unknown'
            job.host_game = ''

        # Generate title ID
        game_id_4char = game_id[:4] if len(game_id) >= 4 else game_id
        title_id_hex = game_id_4char.encode('ascii').hex().upper()

        system_type = game_info.get('system', 'wii')
        if system_type == 'gc':
            job.title_id = f"00050002{title_id_hex}"
        else:
            job.title_id = f"00050000{title_id_hex}"

    def download_icon_for_job(self, job: BatchBuildJob):
        """Download icon and banner for a job from local or remote repository."""
        import urllib.request
        import urllib.error
        import ssl
        from .game_tdb import GameTdb
        from .resources import resources
        import shutil

        game_id = job.game_info.get('game_id', '')
        if not game_id or len(game_id) < 4:
            print(f"  [SKIP] Invalid game ID: {game_id}")
            return False

        repo_id = game_id[:4]
        full_id = game_id[:6] if len(game_id) >= 6 else game_id
        system_type = job.game_info.get('system', 'wii')

        # Use permanent cache directory (not temp - survives across builds)
        cache_dir = paths.images_cache / game_id
        cache_dir.mkdir(parents=True, exist_ok=True)

        cached_icon = cache_dir / "icon.png"
        cached_banner = cache_dir / "banner.png"
        cached_drc = cache_dir / "drc.png"

        if cached_icon.exists() and cached_banner.exists():
            print(f"  [CACHE] Found cached images for {game_id}")
            job.icon_path = cached_icon
            job.banner_path = cached_banner
            if cached_drc.exists():
                job.drc_path = cached_drc
            else:
                job.drc_path = cached_banner  # Use banner as DRC
            return True

        # First check local resources/wii/ directory
        local_wii_dir = resources.resources_dir / "wii"
        if local_wii_dir.exists():
            local_icon = local_wii_dir / "banner" / f"{repo_id}.png"
            local_banner = local_wii_dir / "banner" / f"{repo_id}.png"

            if local_icon.exists() and local_banner.exists():
                print(f"  [LOCAL] Found local images for {repo_id}")
                cache_dir.mkdir(parents=True, exist_ok=True)

                # Copy icon
                icon_path = cache_dir / "icon.png"
                shutil.copy(local_icon, icon_path)
                job.icon_path = icon_path

                # Copy banner
                banner_path = cache_dir / "banner.png"
                shutil.copy(local_banner, banner_path)
                job.banner_path = banner_path

                return True

        # If not found locally, try remote download
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Try exact game_id first (highest priority), then full_id, then alternatives
        alternative_ids = [game_id]  # Start with exact game ID
        if full_id != game_id and full_id != repo_id:
            alternative_ids.append(full_id)
        # Only use alternatives as fallback
        alternative_ids.extend(list(GameTdb.get_alternative_ids(repo_id)))

        download_success = False
        from PIL import Image
        import io

        # Try GameTDB first (coverfullHQ for banner, cover for icon crop)
        # Prioritize by region code in game ID
        region_char = game_id[3] if len(game_id) >= 4 else 'E'
        if region_char == 'K':
            region_codes = ['KO', 'EN', 'US', 'JA']
        elif region_char == 'J':
            region_codes = ['JA', 'EN', 'US', 'KO']
        elif region_char == 'P':
            region_codes = ['EN', 'US', 'JA', 'KO']
        else:  # E or others
            region_codes = ['US', 'EN', 'JA', 'KO']

        for try_id in alternative_ids:
            for region in region_codes:
                # Full cover for banner (front+back+spine)
                fullcover_url = f"https://art.gametdb.com/wii/coverfullHQ/{region}/{try_id}.png"
                # Regular cover for icon (just front)
                cover_url = f"https://art.gametdb.com/wii/cover/{region}/{try_id}.png"

                try:
                    # Download full cover for banner and DRC
                    req = urllib.request.Request(
                        fullcover_url,
                        headers={'User-Agent': 'WiiVC-Injector/1.0'}
                    )
                    with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
                        banner_data = response.read()

                        # Resize for banner (1280x720)
                        img = Image.open(io.BytesIO(banner_data))
                        banner_img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                        banner_path = cache_dir / "banner.png"
                        banner_img.save(banner_path)
                        job.banner_path = banner_path

                        # Resize for DRC (854x480)
                        drc_img = img.resize((854, 480), Image.Resampling.LANCZOS)
                        drc_path = cache_dir / "drc.png"
                        drc_img.save(drc_path)
                        job.drc_path = drc_path

                    # Download cover and crop top portion for icon
                    req = urllib.request.Request(
                        cover_url,
                        headers={'User-Agent': 'WiiVC-Injector/1.0'}
                    )
                    with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
                        cover_data = response.read()

                        # Crop top portion of cover for icon
                        img = Image.open(io.BytesIO(cover_data))
                        width, height = img.size

                        # Crop top square portion (width x width from top)
                        crop_size = min(width, height)
                        cropped = img.crop((0, 0, width, crop_size))

                        # Resize to icon size (128x128)
                        icon_img = cropped.resize((128, 128), Image.Resampling.LANCZOS)

                        icon_path = cache_dir / "icon.png"
                        icon_img.save(icon_path)
                        job.icon_path = icon_path

                    print(f"  [OK] Downloaded from GameTDB for {try_id} ({region})")
                    download_success = True

                    # Try to get Korean title from GameTDB
                    self.fetch_gametdb_title(job, try_id, ssl_context)
                    return True

                except Exception as e:
                    # Try just cover if fullcover fails
                    try:
                        req = urllib.request.Request(
                            cover_url,
                            headers={'User-Agent': 'WiiVC-Injector/1.0'}
                        )
                        with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
                            cover_data = response.read()

                            # Use cover for both
                            img = Image.open(io.BytesIO(cover_data))
                            width, height = img.size

                            # Crop top for icon
                            crop_size = min(width, height)
                            cropped = img.crop((0, 0, width, crop_size))
                            icon_img = cropped.resize((128, 128), Image.Resampling.LANCZOS)
                            icon_path = cache_dir / "icon.png"
                            icon_img.save(icon_path)
                            job.icon_path = icon_path

                            # Resize for banner (1280x720)
                            banner_img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                            banner_path = cache_dir / "banner.png"
                            banner_img.save(banner_path)
                            job.banner_path = banner_path

                            # Resize for DRC (854x480)
                            drc_img = img.resize((854, 480), Image.Resampling.LANCZOS)
                            drc_path = cache_dir / "drc.png"
                            drc_img.save(drc_path)
                            job.drc_path = drc_path

                            print(f"  [OK] Downloaded cover from GameTDB for {try_id} ({region})")
                            download_success = True

                            # Try to get Korean title from GameTDB
                            self.fetch_gametdb_title(job, try_id, ssl_context)
                            return True
                    except:
                        continue

        # Fallback to UWUVCI-IMAGES
        if not download_success:
            for try_id in alternative_ids:
                icon_url = f"https://raw.githubusercontent.com/UWUVCI-PRIME/UWUVCI-IMAGES/master/{system_type}/{try_id}/iconTex.png"
                banner_url = f"https://raw.githubusercontent.com/UWUVCI-PRIME/UWUVCI-IMAGES/master/{system_type}/{try_id}/bootTvTex.png"

                try:
                    # Download icon
                    req = urllib.request.Request(
                        icon_url,
                        headers={'User-Agent': 'WiiVC-Injector/1.0'}
                    )
                    with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
                        icon_data = response.read()
                        icon_path = cache_dir / "icon.png"
                        icon_path.write_bytes(icon_data)
                        job.icon_path = icon_path

                    # Download banner
                    req = urllib.request.Request(
                        banner_url,
                        headers={'User-Agent': 'WiiVC-Injector/1.0'}
                    )
                    with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
                        banner_data = response.read()
                        banner_path = cache_dir / "banner.png"
                        banner_path.write_bytes(banner_data)
                        job.banner_path = banner_path

                        # Resize banner for DRC (854x480)
                        banner_img = Image.open(io.BytesIO(banner_data))
                        drc_img = banner_img.resize((854, 480), Image.Resampling.LANCZOS)
                        drc_path = cache_dir / "drc.png"
                        drc_img.save(drc_path)
                        job.drc_path = drc_path

                    print(f"  [OK] Downloaded from UWUVCI for {try_id}")
                    download_success = True
                    return True

                except:
                    continue

        # If download failed, use default images
        if not download_success:
            print(f"  [DEFAULT] Using default images for {game_id}")
            default_icon = resources.resources_dir / "images" / "default_icon.png"
            default_banner = resources.resources_dir / "images" / "default_banner.png"
            default_drc = resources.resources_dir / "images" / "default_drc.png"

            cache_dir.mkdir(parents=True, exist_ok=True)

            if default_icon.exists():
                icon_path = cache_dir / "icon.png"
                shutil.copy(default_icon, icon_path)
                job.icon_path = icon_path

            if default_banner.exists():
                banner_path = cache_dir / "banner.png"
                shutil.copy(default_banner, banner_path)
                job.banner_path = banner_path

            if default_drc.exists():
                drc_path = cache_dir / "drc.png"
                shutil.copy(default_drc, drc_path)
                job.drc_path = drc_path

        # Images are already saved to cache_dir during download, no need to copy again
        return True

    def fetch_gametdb_title(self, job: BatchBuildJob, game_id: str, ssl_context):
        """Fetch Korean title from GameTDB. Falls back to DB title if not found."""
        import urllib.request
        import re

        try:
            # GameTDB game page
            url = f"https://www.gametdb.com/Wii/{game_id}"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'WiiVC-Injector/1.0'}
            )
            with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
                html = response.read().decode('utf-8', errors='ignore')

                # Look for Korean title - pattern: title (KO)</td><td...>쿠킹 마마</td>
                ko_match = re.search(r'title\s*\(KO\)</td><td[^>]*>([^<]+)</td>', html)
                if ko_match:
                    ko_title = ko_match.group(1).strip()
                    if ko_title:
                        job.title_name = ko_title
                        print(f"  [TITLE] GameTDB Korean: {ko_title}")
                        return

                # Fallback to EN title - pattern: title (EN)</td><td...>Cooking Mama</td>
                en_match = re.search(r'title\s*\(EN\)</td><td[^>]*>([^<]+)</td>', html)
                if en_match:
                    en_title = en_match.group(1).strip()
                    if en_title:
                        job.title_name = en_title
                        print(f"  [TITLE] GameTDB English: {en_title}")
                        return

                # No title found on GameTDB, keep DB title
                print(f"  [TITLE] No GameTDB title, using DB: {job.title_name}")

        except Exception as e:
            # Keep DB title if fetch fails
            db_title = getattr(job, 'db_title', job.title_name)
            print(f"  [TITLE] GameTDB failed ({e}), using DB: {db_title}")


class SimpleKeysDialog(QDialog):
    """Simple dialog for entering encryption keys."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Remove ? button from title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self.load_existing_settings()

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle(tr.get("encryption_keys"))
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Common Key
        self.common_key_input = QLineEdit()
        self.common_key_input.setPlaceholderText(tr.get("common_key_placeholder"))
        form.addRow(tr.get("wii_u_common_key"), self.common_key_input)

        # Title Keys
        self.rhythm_key_input = QLineEdit()
        self.rhythm_key_input.setPlaceholderText("필수 - Rhythm Heaven Fever (USA)")
        form.addRow("Rhythm Heaven Fever:", self.rhythm_key_input)

        self.xenoblade_key_input = QLineEdit()
        self.xenoblade_key_input.setPlaceholderText("선택 - Xenoblade Chronicles (USA)")
        form.addRow("Xenoblade Chronicles:", self.xenoblade_key_input)

        self.galaxy_key_input = QLineEdit()
        self.galaxy_key_input.setPlaceholderText("선택 - Super Mario Galaxy 2 (EUR)")
        form.addRow("Mario Galaxy 2:", self.galaxy_key_input)

        layout.addLayout(form)

        # Output directory setting
        output_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText(tr.get("output_folder_placeholder"))
        browse_btn = QPushButton(tr.get("browse"))
        browse_btn.clicked.connect(self.browse_output_dir)
        clear_btn = QPushButton(tr.get("clear"))
        clear_btn.clicked.connect(self.clear_output_dir)
        output_layout.addWidget(self.output_dir_input)
        output_layout.addWidget(browse_btn)
        output_layout.addWidget(clear_btn)

        output_label = QLabel(tr.get("output_folder"))
        layout.addWidget(output_label)
        layout.addLayout(output_layout)

        # Info label
        if tr.current_language == "ko":
            info_text = "참고: Rhythm Heaven 키는 필수입니다. 나머지는 선택사항이며 없으면 Rhythm Heaven으로 빌드됩니다."
        else:
            info_text = "Note: Rhythm Heaven key is required. Others are optional, will fallback to Rhythm Heaven if not set."
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 11px; margin: 10px 0;")
        layout.addWidget(info_label)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(tr.get("save"))
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton(tr.get("cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_output_dir(self):
        """Browse for output directory."""
        dialog_title = tr.get("output_folder").replace(":", "")
        output_dir = QFileDialog.getExistingDirectory(self, dialog_title)
        if output_dir:
            self.output_dir_input.setText(output_dir)

    def clear_output_dir(self):
        """Clear output directory setting to use default."""
        self.output_dir_input.clear()

    def save(self):
        """Save keys and close."""
        import json

        common_key = self.common_key_input.text().strip()
        if not common_key:
            error_msg = "Wii U Common Key가 필요합니다!" if tr.current_language == "ko" else "Wii U Common Key is required!"
            show_message(self, "warning", tr.get("error"), error_msg)
            return

        # Check if at least Rhythm Heaven key is provided (required)
        rhythm_key = self.rhythm_key_input.text().strip()
        xenoblade_key = self.xenoblade_key_input.text().strip()
        galaxy_key = self.galaxy_key_input.text().strip()

        if not rhythm_key:
            error_msg = "Rhythm Heaven Fever 타이틀 키는 필수입니다!" if tr.current_language == "ko" else "Rhythm Heaven Fever title key is required!"
            show_message(self, "warning", tr.get("error"), error_msg)
            return

        # Save to settings file
        output_dir = self.output_dir_input.text().strip()
        settings = {
            'wii_u_common_key': common_key,
            'title_key_rhythm_heaven': rhythm_key,
            'title_key_xenoblade': xenoblade_key,
            'title_key_galaxy2': galaxy_key,
            'output_directory': output_dir
        }

        settings_file = Path.home() / ".wiivc_injector_settings.json"
        print(f"[DEBUG] Saving settings to: {settings_file}")
        print(f"[DEBUG] Settings: {settings}")

        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Settings saved successfully")
        except Exception as e:
            print(f"[ERROR] Failed to save settings: {e}")
            import traceback
            traceback.print_exc()
            error_msg = f"설정 저장 실패: {e}" if tr.current_language == "ko" else f"Failed to save settings: {e}"
            show_message(self, "warning", tr.get("error"), error_msg)
            return

        self.accept()

    def load_existing_settings(self):
        """Load existing settings from file."""
        import json

        settings_file = Path.home() / ".wiivc_injector_settings.json"
        if not settings_file.exists():
            return

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

                # Fill in existing values
                common_key = settings.get('wii_u_common_key', '')
                if common_key:
                    self.common_key_input.setText(common_key)

                rhythm_key = settings.get('title_key_rhythm_heaven', '')
                if rhythm_key:
                    self.rhythm_key_input.setText(rhythm_key)

                xenoblade_key = settings.get('title_key_xenoblade', '')
                if xenoblade_key:
                    self.xenoblade_key_input.setText(xenoblade_key)

                galaxy_key = settings.get('title_key_galaxy2', '')
                if galaxy_key:
                    self.galaxy_key_input.setText(galaxy_key)

                output_dir = settings.get('output_directory', '')
                if output_dir:
                    self.output_dir_input.setText(output_dir)

                print("[DEBUG] Loaded existing settings into dialog")
        except Exception as e:
            print(f"[WARN] Failed to load existing settings: {e}")


class EditGameDialog(QDialog):
    """Dialog to edit individual game metadata."""

    def __init__(self, job: BatchBuildJob, available_bases: dict = None, parent=None):
        super().__init__(parent)
        # Remove ? button from title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.job = job
        self.available_bases = available_bases or {}
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        title_text = "게임 메타데이터 편집" if tr.current_language == "ko" else "Edit Game Metadata"
        self.setWindowTitle(title_text)
        self.setMinimumWidth(600)

        layout = QVBoxLayout(self)

        # Image previews
        images_layout = QHBoxLayout()

        # Icon preview (128x128 original size, display larger)
        icon_layout = QVBoxLayout()
        icon_label_text = "아이콘 (클릭하여 변경)" if tr.current_language == "ko" else "Icon (Click to change)"
        icon_layout.addWidget(QLabel(icon_label_text))
        self.icon_preview = QLabel()
        self.icon_preview.setFixedSize(192, 192)
        self.icon_preview.setStyleSheet("border: 2px solid #ccc; background: #f0f0f0;")
        self.icon_preview.setAlignment(Qt.AlignCenter)
        if self.job.icon_path and self.job.icon_path.exists():
            print(f"[DEBUG] Loading icon from: {self.job.icon_path}")
            pixmap = QPixmap(str(self.job.icon_path))
            if not pixmap.isNull():
                self.icon_preview.setPixmap(pixmap.scaled(192, 192, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                print(f"[ERROR] Failed to load icon pixmap from: {self.job.icon_path}")
                no_image_text = "이미지 로드 실패" if tr.current_language == "ko" else "Failed to load image"
                self.icon_preview.setText(no_image_text)
        else:
            print(f"[DEBUG] Icon path not found or doesn't exist: {self.job.icon_path}")
            no_image_text = "이미지 없음\n클릭하여 선택" if tr.current_language == "ko" else "No Image\nClick to select"
            self.icon_preview.setText(no_image_text)
        self.icon_preview.mousePressEvent = lambda e: self.change_icon()
        self.icon_preview.setCursor(Qt.PointingHandCursor)
        icon_layout.addWidget(self.icon_preview)
        images_layout.addLayout(icon_layout)

        # Banner preview (1280x720 original, display scaled)
        banner_layout = QVBoxLayout()
        banner_label_text = "배너 (클릭하여 변경)" if tr.current_language == "ko" else "Banner (Click to change)"
        banner_layout.addWidget(QLabel(banner_label_text))
        self.banner_preview = QLabel()
        self.banner_preview.setFixedSize(384, 216)
        self.banner_preview.setStyleSheet("border: 2px solid #ccc; background: #f0f0f0;")
        self.banner_preview.setAlignment(Qt.AlignCenter)
        if self.job.banner_path and self.job.banner_path.exists():
            print(f"[DEBUG] Loading banner from: {self.job.banner_path}")
            pixmap = QPixmap(str(self.job.banner_path))
            if not pixmap.isNull():
                self.banner_preview.setPixmap(pixmap.scaled(384, 216, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                print(f"[ERROR] Failed to load banner pixmap from: {self.job.banner_path}")
                no_image_text = "이미지 로드 실패" if tr.current_language == "ko" else "Failed to load image"
                self.banner_preview.setText(no_image_text)
        else:
            print(f"[DEBUG] Banner path not found or doesn't exist: {self.job.banner_path}")
            no_image_text = "이미지 없음\n클릭하여 선택" if tr.current_language == "ko" else "No Image\nClick to select"
            self.banner_preview.setText(no_image_text)
        self.banner_preview.mousePressEvent = lambda e: self.change_banner()
        self.banner_preview.setCursor(Qt.PointingHandCursor)
        banner_layout.addWidget(self.banner_preview)
        images_layout.addLayout(banner_layout)

        layout.addLayout(images_layout)

        # Title
        title_layout = QHBoxLayout()
        game_title_text = "게임 제목:" if tr.current_language == "ko" else "Game Title:"
        title_layout.addWidget(QLabel(game_title_text))
        self.title_input = QLineEdit(self.job.title_name)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        # Title ID (read-only, for reference/copy only)
        id_layout = QHBoxLayout()
        title_id_text = "타이틀 ID:" if tr.current_language == "ko" else "Title ID:"
        id_layout.addWidget(QLabel(title_id_text))
        self.id_input = QLineEdit(self.job.title_id)
        self.id_input.setReadOnly(True)  # Make read-only (can still copy text)
        self.id_input.setStyleSheet("background-color: #f5f5f5;")  # Visual indicator
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)

        # Base ROM Selection (only if multiple bases available)
        if self.available_bases:
            base_layout = QHBoxLayout()
            base_label_text = "베이스 롬:" if tr.current_language == "ko" else "Base ROM:"
            base_label = QLabel(base_label_text)
            base_layout.addWidget(base_label)
            self.base_combo = QComboBox()

            # Add available bases to combo box
            for base_name in self.available_bases.keys():
                self.base_combo.addItem(base_name)

            # Set current selection (default to current host_game or first available)
            if self.job.host_game and self.job.host_game in self.available_bases:
                self.base_combo.setCurrentText(self.job.host_game)

            base_layout.addWidget(self.base_combo, 1)  # Add stretch factor to combo box
            layout.addLayout(base_layout)
        else:
            self.base_combo = None

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(tr.get("save"))
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton(tr.get("cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def change_icon(self):
        """Change icon image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "아이콘 이미지 선택" if tr.current_language == "ko" else "Select Icon Image",
            "",
            "Images (*.png *.jpg *.jpeg);;All Files (*.*)"
        )
        if file_path:
            self.job.icon_path = Path(file_path)
            pixmap = QPixmap(file_path)
            self.icon_preview.setPixmap(pixmap.scaled(192, 192, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def change_banner(self):
        """Change banner image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "배너 이미지 선택" if tr.current_language == "ko" else "Select Banner Image",
            "",
            "Images (*.png *.jpg *.jpeg);;All Files (*.*)"
        )
        if file_path:
            self.job.banner_path = Path(file_path)
            pixmap = QPixmap(file_path)
            self.banner_preview.setPixmap(pixmap.scaled(384, 216, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def save(self):
        """Save changes."""
        self.job.title_name = self.title_input.text()
        # Title ID is read-only, don't save it
        # self.job.title_id = self.id_input.text()

        # Save selected base ROM if combo box exists
        if self.base_combo:
            self.job.host_game = self.base_combo.currentText()

        self.accept()


class CompatibilityListDialog(QDialog):
    """Dialog to show compatibility list from database."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Remove ? button from title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize UI."""
        title_text = "호환성 목록" if tr.current_language == "ko" else "Compatibility List"
        self.setWindowTitle(title_text)
        self.setMinimumSize(1050, 700)

        layout = QVBoxLayout(self)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("검색:" if tr.current_language == "ko" else "Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("게임 이름 또는 ID 입력..." if tr.current_language == "ko" else "Enter game name or ID...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        if tr.current_language == "ko":
            headers = ["게임 ID", "게임 제목", "지역", "게임패드 호환", "호스트 게임"]
        else:
            headers = ["Game ID", "Game Title", "Region", "Gamepad Compat", "Host Game"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(2, 60)
        self.table.setColumnWidth(3, 150)  # Gamepad Compat - fixed size
        self.table.setColumnWidth(4, 150)  # Host Game - fixed size
        # Use stretch for title column only
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Game Title
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # Allow editing only game_id column (column 0)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("저장" if tr.current_language == "ko" else "Save")
        save_btn.clicked.connect(self.save_changes)
        btn_layout.addWidget(save_btn)

        close_btn = QPushButton(tr.get("close") if tr.current_language == "ko" else "Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        self.changes = {}  # Track changes: {(title, region): new_game_id}

    def load_data(self):
        """Load data from compatibility database."""
        # Fill missing game IDs from GameTDB first
        updated = compatibility_db.fill_missing_game_ids()
        if updated > 0:
            print(f"[DB] Updated {updated} missing game IDs from GameTDB")

        games = compatibility_db.get_all_games()
        self.all_games = games

        self.table.setRowCount(len(games))
        for row, game in enumerate(games):
            self.table.setItem(row, 0, QTableWidgetItem(game.get('game_id', '')))
            self.table.setItem(row, 1, QTableWidgetItem(game.get('title', '')))
            self.table.setItem(row, 2, QTableWidgetItem(game.get('region', '')))

            # Gamepad compatibility with color
            gamepad = game.get('gamepad_compatibility', 'Unknown')
            gamepad_item = QTableWidgetItem(gamepad)
            if 'works' in gamepad.lower() and 'doesn\'t' not in gamepad.lower():
                gamepad_item.setBackground(QColor(200, 255, 200))
            elif 'unknown' in gamepad.lower():
                gamepad_item.setBackground(QColor(220, 220, 220))
            else:
                gamepad_item.setBackground(QColor(255, 200, 200))
            self.table.setItem(row, 3, gamepad_item)

            self.table.setItem(row, 4, QTableWidgetItem(game.get('host_game', '')))

    def on_item_changed(self, item):
        """Track changes to game_id or title column."""
        row = item.row()
        if item.column() == 0:  # game_id column
            title_item = self.table.item(row, 1)
            region_item = self.table.item(row, 2)
            if title_item and region_item:
                # Use original title from all_games
                orig_title = self.all_games[row]['title']
                region = region_item.text()
                key = ('game_id', orig_title, region)
                self.changes[key] = item.text()
        elif item.column() == 1:  # title column
            region_item = self.table.item(row, 2)
            if region_item:
                orig_title = self.all_games[row]['title']
                region = region_item.text()
                key = ('title', orig_title, region)
                self.changes[key] = item.text()

    def save_changes(self):
        """Save all changes to database."""
        if not self.changes:
            msg = "변경사항이 없습니다." if tr.current_language == "ko" else "No changes to save."
            show_message(self, "info", "Info", msg)
            return

        for key, value in self.changes.items():
            change_type, orig_title, region = key
            if change_type == 'game_id':
                compatibility_db.update_game_id(orig_title, region, value)
            elif change_type == 'title':
                compatibility_db.update_title(orig_title, region, value)

        count = len(self.changes)
        self.changes.clear()

        # Reload data to reflect changes
        self.load_data()

        msg = f"{count}개 항목이 저장되었습니다." if tr.current_language == "ko" else f"{count} item(s) saved."
        show_message(self, "info", "Info", msg)

    def filter_table(self, text):
        """Filter table by search text."""
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)


class BatchWindow(QMainWindow):
    """Simplified batch build window."""

    def __init__(self):
        super().__init__()
        self.jobs = []
        self.batch_builder = None
        self.loader_thread = None
        self.available_bases = {}  # Will be populated from settings
        self.init_ui()
        self.load_available_bases()  # Load on startup

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle(tr.get("app_title") + " - " + (tr.get("batch_converter_title") if tr.current_language == "ko" else "Batch Mode"))
        self.setGeometry(100, 100, 800, 500)  # 타이틀 ID 컬럼 제거로 너비 복원

        # Set window icon
        import sys
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            icon_path = Path(sys._MEIPASS) / "resources" / "images" / "icon.png"
        else:
            # Running as script
            icon_path = Path(__file__).parent.parent.parent / "resources" / "images" / "icon.png"

        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Top controls
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        # Modern button style
        btn_style = """
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ddd;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #bbb;
            }
            QPushButton:pressed {
                background-color: #ddd;
            }
        """

        self.add_btn = QPushButton(tr.get("add_files"))
        self.add_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        self.add_btn.setStyleSheet(btn_style)
        self.add_btn.clicked.connect(self.add_games)
        top_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton(tr.get("remove_selected"))
        self.remove_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.remove_btn.setStyleSheet(btn_style)
        self.remove_btn.clicked.connect(self.remove_selected)
        top_layout.addWidget(self.remove_btn)

        self.clear_btn = QPushButton(tr.get("clear_all"))
        self.clear_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.clear_btn.setStyleSheet(btn_style)
        self.clear_btn.clicked.connect(self.clear_all)
        top_layout.addWidget(self.clear_btn)

        # Compatibility list button
        compat_text = "호환성 목록" if tr.current_language == "ko" else "Compatibility"
        self.compat_btn = QPushButton(compat_text)
        self.compat_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.compat_btn.setStyleSheet(btn_style)
        self.compat_btn.clicked.connect(self.show_compatibility_list)
        top_layout.addWidget(self.compat_btn)

        top_layout.addStretch()

        # Settings button
        settings_text = "⚙ 설정" if tr.current_language == "ko" else "⚙ Settings"
        self.settings_btn = QPushButton(settings_text)
        self.settings_btn.setStyleSheet(btn_style)
        self.settings_btn.clicked.connect(self.show_settings)
        top_layout.addWidget(self.settings_btn)

        auto_download_text = "아이콘 자동 다운로드" if tr.current_language == "ko" else "Auto Download Icons"
        self.auto_icons_check = QCheckBox(auto_download_text)
        self.auto_icons_check.setChecked(True)
        top_layout.addWidget(self.auto_icons_check)

        keep_temp_text = "임시 파일 유지" if tr.current_language == "ko" else "Keep Temp Files"
        self.keep_temp_check = QCheckBox(keep_temp_text)
        self.keep_temp_check.setChecked(False) # Default to not keeping temp files
        top_layout.addWidget(self.keep_temp_check)
        self.keep_temp_check.setVisible(False)

        layout.addLayout(top_layout)

        # Game list table (파일명/게임제목 통합, 게임 ID 별도 표시, 호환성/패드옵션 통합)
        self.table = QTableWidget()
        self.table.setColumnCount(7)

        if tr.current_language == "ko":
            headers = ["게임 제목 / 파일명", "게임 ID", "아이콘", "배너", "호환성 / 패드옵션", "상태", "작업"]
        else:
            headers = ["Game Title / Filename", "Game ID", "Icon", "Banner", "Compatibility / Pad Option", "Status", "Actions"]

        self.table.setHorizontalHeaderLabels(headers)
        # Header styling - modern flat design with vertical separators
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                border: none;
                border-right: 1px solid #d0d0d0;
                border-bottom: 2px solid #4a90e2;
                padding: 8px 4px;
                font-weight: 500;
                text-align: center;
            }
            QHeaderView::section:first {
                padding-left: 15px;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        # Set column widths (파일명/게임제목 통합, 게임 ID 별도, 호환성/패드옵션 통합)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # File Name / Game Title
        # 첫 번째 헤더만 좌측 정렬
        header_item = self.table.horizontalHeaderItem(0)
        if header_item:
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setColumnWidth(1, 80)   # Game ID
        self.table.setColumnWidth(2, 60)   # Icon preview
        self.table.setColumnWidth(3, 90)   # Banner preview
        self.table.setColumnWidth(4, 150)  # Compatibility / Pad Option (통합 컬럼, 180→150)
        self.table.setColumnWidth(5, 80)   # Status
        self.table.setColumnWidth(6, 80)   # Actions
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # 아이콘/배너 컬럼 중앙 정렬을 위한 스타일시트
        self.table.setStyleSheet("""
            QTableWidget::item {
                padding: 2px;
            }
        """)
        # 더블클릭 편집 제거 - 편집 버튼에서만 수정 가능
        # self.table.cellDoubleClicked.connect(self.edit_game)
        self.table.cellClicked.connect(self.on_cell_clicked)
        # 셀 편집 불가능하게 설정
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Progress
        progress_layout = QVBoxLayout()
        ready_text = "준비 완료 - 게임을 추가하세요" if tr.current_language == "ko" else "Ready - Add games to start"
        self.status_label = QLabel(ready_text)
        progress_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        layout.addLayout(progress_layout)

        # Bottom controls
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        build_text = "빌드" if tr.current_language == "ko" else "Start Build"
        self.build_btn = QPushButton(build_text)
        self.build_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb85c, stop:1 #4cae4c);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 24px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6cc76c, stop:1 #5cb85c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a9d4a, stop:1 #3d8b3d);
            }
            QPushButton:disabled {
                background: #e0e0e0;
                color: #999;
            }
        """)
        self.build_btn.clicked.connect(self.start_batch_build)
        self.build_btn.setEnabled(False)
        bottom_layout.addWidget(self.build_btn)

        stop_text = "■ 중지" if tr.current_language == "ko" else "■ Stop"
        self.stop_btn = QPushButton(stop_text)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b, stop:1 #ee5555);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 20px;
                border: 1px solid #dd4444;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5555, stop:1 #ee3333);
                color: white;
                border-color: #cc2222;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ee3333, stop:1 #dd2222);
            }
            QPushButton:disabled {
                background: #f0f0f0;
                color: #bbb;
                border-color: #ddd;
            }
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_build)
        bottom_layout.addWidget(self.stop_btn)

        layout.addLayout(bottom_layout)

    def add_games(self):
        """Add game files to batch queue asynchronously."""
        if tr.current_language == "ko":
            dialog_title = "게임 파일 선택"
            file_filter = "게임 파일 (*.iso *.wbfs *.nkit.iso *.iso.dec *.gcm);;모든 파일 (*.*)"
        else:
            dialog_title = "Select Game Files"
            file_filter = "Game Files (*.iso *.wbfs *.nkit.iso *.iso.dec *.gcm);;All Files (*.*)"

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            dialog_title,
            "",
            file_filter
        )

        if not file_paths:
            return

        # Filter out duplicates
        existing_paths = {str(job.game_path.resolve()) for job in self.jobs}
        new_file_paths = []
        duplicate_count = 0

        for file_path in file_paths:
            resolved_path = str(Path(file_path).resolve())
            if resolved_path in existing_paths:
                duplicate_count += 1
                print(f"[SKIP] Duplicate file: {Path(file_path).name}")
            else:
                new_file_paths.append(file_path)
                existing_paths.add(resolved_path)

        if duplicate_count > 0:
            if tr.current_language == "ko":
                msg = f"{duplicate_count}개 중복 파일을 건너뛰었습니다."
                title = "중복 파일"
            else:
                msg = f"{duplicate_count} duplicate files were skipped."
                title = "Duplicates"
            show_message(self, "info", title, msg)

        if not new_file_paths:
            return

        # Show loading status
        if tr.current_language == "ko":
            self.status_label.setText(f"{len(new_file_paths)}개 게임 로딩 중...")
        else:
            self.status_label.setText(f"Loading {len(new_file_paths)} games...")

        # Create progress dialog
        progress_label = tr.get("loading_games_message")
        window_title = tr.get("loading_games_title")
        cancel_label = tr.get("cancel")

        self.loading_progress = QProgressDialog(
            progress_label,
            cancel_label,
            0,
            len(new_file_paths),
            self
        )
        # Set window title and remove help button from title bar
        self.loading_progress.setWindowTitle(window_title)
        self.loading_progress.setWindowFlags(self.loading_progress.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.loading_progress.setWindowModality(Qt.WindowModal)
        self.loading_progress.setMinimumDuration(500)  # Show after 500ms
        self.loading_progress.setMinimumWidth(500)  # Set wider progress bar
        self.loading_progress.canceled.connect(self.cancel_loading)

        # Start background loading thread
        self.loader_thread = GameLoaderThread(
            new_file_paths,
            self.auto_icons_check.isChecked()
        )
        self.loader_thread.game_loaded.connect(self.on_game_loaded)
        self.loader_thread.loading_finished.connect(self.on_loading_finished)
        self.loader_thread.progress_updated.connect(self.on_loading_progress)
        self.loader_thread.start()

    def cancel_loading(self):
        """Cancel game loading."""
        if self.loader_thread:
            self.loader_thread.stop()
            if tr.current_language == "ko":
                self.status_label.setText("로딩 취소됨")
            else:
                self.status_label.setText("Loading canceled")

    def on_loading_progress(self, current, total):
        """Update loading progress."""
        if hasattr(self, 'loading_progress') and self.loading_progress is not None:
            try:
                self.loading_progress.setValue(current)
                self.loading_progress.setLabelText(tr.get("loading_games_progress", current=current, total=total))
            except (AttributeError, RuntimeError) as e:
                # Dialog might be closed/deleted - ignore
                pass

    def on_game_loaded(self, job: BatchBuildJob):
        """Handle when a game is loaded (called for each game as it finishes)."""
        # Add job to list
        self.jobs.append(job)

        # Add to table immediately
        row_index = self.add_job_to_table(job)

        # Update icon if already downloaded
        self.update_icon_preview(row_index, job)

        # Update status
        if tr.current_language == "ko":
            self.status_label.setText(f"{len(self.jobs)}개 게임 로드됨... (계속 로딩 중...)")
        else:
            self.status_label.setText(f"Loaded {len(self.jobs)} games...")
        self.update_ui_state()

    def on_loading_finished(self, total_loaded):
        """Handle when all games are loaded."""
        # Close progress dialog
        if hasattr(self, 'loading_progress'):
            self.loading_progress.close()
            delattr(self, 'loading_progress')

        if tr.current_language == "ko":
            self.status_label.setText(f"준비 완료 - {total_loaded}개 게임 로드됨")
        else:
            self.status_label.setText(f"Ready - {total_loaded} games loaded")
        self.loader_thread = None
        self.update_ui_state()

    def update_icon_preview(self, row: int, job: BatchBuildJob):
        """Update icon and banner preview in table."""
        # Update icon (Column 2) - Use QLabel for center alignment
        if job.icon_path and job.icon_path.exists():
            pixmap = QPixmap(str(job.icon_path))
            scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label = QLabel()
            icon_label.setPixmap(scaled_pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 2, icon_label)
        else:
            # Create a red X icon for failed download
            icon_item = QTableWidgetItem("X")
            icon_item.setTextAlignment(Qt.AlignCenter)
            icon_item.setForeground(QColor(255, 0, 0))
            font = QFont()
            font.setPointSize(24)
            font.setBold(True)
            icon_item.setFont(font)
            icon_item.setBackground(QColor(255, 240, 240))
            self.table.setItem(row, 2, icon_item)

        # Update banner (Column 3) - Use QLabel for center alignment
        if job.banner_path and job.banner_path.exists():
            pixmap = QPixmap(str(job.banner_path))
            scaled_pixmap = pixmap.scaled(72, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            banner_label = QLabel()
            banner_label.setPixmap(scaled_pixmap)
            banner_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 3, banner_label)
        else:
            # Create a red X for failed banner
            banner_item = QTableWidgetItem("X")
            banner_item.setTextAlignment(Qt.AlignCenter)
            banner_item.setForeground(QColor(255, 0, 0))
            font = QFont()
            font.setPointSize(20)
            font.setBold(True)
            banner_item.setFont(font)
            banner_item.setBackground(QColor(255, 240, 240))
            self.table.setItem(row, 3, banner_item)

    def add_job_to_table(self, job: BatchBuildJob):
        """Add job to table and return row index."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 50)  # Height for two-line cells

        # Column 0: Game title / File name (Combined)
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(4, 2, 4, 2)
        title_layout.setSpacing(2)

        # Game title (top)
        title_label = QLabel(job.title_name)
        title_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #000;")
        title_layout.addWidget(title_label)

        # File name (bottom)
        filename_label = QLabel(job.game_path.name)
        filename_label.setStyleSheet("font-size: 11px; color: #666;")
        title_layout.addWidget(filename_label)

        self.table.setCellWidget(row, 0, title_widget)

        # Column 1: Game ID
        game_id = job.game_info.get('game_id', '') if job.game_info else ''
        game_id_item = QTableWidgetItem(game_id)
        game_id_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, game_id_item)

        # Column 2: Icon preview (will be replaced by QLabel in update_icon_preview)
        icon_item = QTableWidgetItem("")
        self.table.setItem(row, 2, icon_item)

        # Column 3: Banner preview (will be replaced by QLabel in update_icon_preview)
        banner_item = QTableWidgetItem("")
        self.table.setItem(row, 3, banner_item)

        # Column 4: Compatibility / Pad Option (Combined)
        # Create widget with vertical layout
        compat_widget = QWidget()
        compat_layout = QVBoxLayout(compat_widget)
        compat_layout.setContentsMargins(4, 2, 4, 2)
        compat_layout.setSpacing(2)

        # Compatibility label (top)
        compat_label = QLabel(job.gamepad_compatibility)
        compat_label.setAlignment(Qt.AlignCenter)
        compat_label.setStyleSheet("font-size: 11px; padding: 1px 4px;")

        # Color code based on compatibility
        if 'works' in job.gamepad_compatibility.lower() and 'doesn\'t' not in job.gamepad_compatibility.lower():
            compat_label.setStyleSheet("background-color: #c8ffc8; font-size: 11px; padding: 1px 4px; border-radius: 3px;")  # Light green
        elif 'classic' in job.gamepad_compatibility.lower() or 'lr' in job.gamepad_compatibility.lower():
            compat_label.setStyleSheet("background-color: #ffffc8; font-size: 11px; padding: 1px 4px; border-radius: 3px;")  # Light yellow
        elif 'unknown' in job.gamepad_compatibility.lower():
            compat_label.setStyleSheet("background-color: #dcdcdc; font-size: 11px; padding: 1px 4px; border-radius: 3px;")  # Light gray
        else:
            compat_label.setStyleSheet("background-color: #ffc8c8; font-size: 11px; padding: 1px 4px; border-radius: 3px;")  # Light red

        compat_layout.addWidget(compat_label)

        # Pad Option ComboBox (bottom) - 7 Controller Profiles
        pad_combo = QComboBox()
        pad_combo.setStyleSheet("font-size: 11px;")
        if tr.current_language == "ko":
            pad_combo.addItems([
                "미적용 (위모트)",          # Profile 1: no_gamepad
                "게임패드 CC",             # Profile 2: none (default)
                "게임패드 CC+LR",          # Profile 3: gamepad_lr
                "게임패드 위모트(↕)",      # Profile 4: wiimote
                "게임패드 위모트(↔)",      # Profile 5: horizontal_wiimote
                "갤럭시 패치(올스타)",     # Profile 6: galaxy_allstars
                "갤럭시 패치(엔비디아)"    # Profile 7: galaxy_nvidia
            ])
        else:
            pad_combo.addItems([
                "No Pad (Wiimote)",        # Profile 1
                "Pad CC",                  # Profile 2
                "Pad CC+LR",               # Profile 3
                "Pad Wiimote(↕)",          # Profile 4
                "Pad Wiimote(↔)",          # Profile 5
                "Galaxy Patch(AllStars)",  # Profile 6
                "Galaxy Patch(Nvidia)"     # Profile 7
            ])

        # Set default based on compatibility from DB
        if 'works' in job.gamepad_compatibility.lower() and 'doesn\'t' not in job.gamepad_compatibility.lower():
            pad_combo.setCurrentIndex(1)  # Gamepad CC (Profile 2)
            job.pad_option = "none"  # 기본 CC 에뮬레이션
        else:
            pad_combo.setCurrentIndex(0)  # No Pad (Profile 1)
            job.pad_option = "no_gamepad"  # 미적용

        pad_combo.currentIndexChanged.connect(lambda idx, r=row: self.on_pad_option_changed(r, idx))
        compat_layout.addWidget(pad_combo)

        self.table.setCellWidget(row, 4, compat_widget)

        # Column 5: Status
        status_text = "대기 중" if tr.current_language == "ko" else "Pending"
        status_item = QTableWidgetItem(status_text)
        status_item.setTextAlignment(Qt.AlignCenter)
        status_item.setBackground(QColor(255, 249, 196))  # Yellow
        self.table.setItem(row, 5, status_item)

        # Column 6: Edit button
        edit_text = "편집" if tr.current_language == "ko" else "Edit"
        edit_btn = QPushButton(edit_text)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #fafafa;
                color: #555;
                border: 1px solid #ddd;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                color: #333;
                border-color: #bbb;
            }
        """)
        edit_btn.clicked.connect(lambda checked, btn=edit_btn: self.edit_game_by_button(btn))
        self.table.setCellWidget(row, 6, edit_btn)

        return row

    def edit_game(self, row, column):
        """Edit game metadata (사용 안 함 - 편집 버튼으로만 수정)."""
        # 더블클릭 편집 비활성화됨
        pass

    def edit_game_by_button(self, button):
        """Edit game by finding the button's row in the table."""
        # Find the row by iterating through all rows to find the button
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 6) == button:
                if row < len(self.jobs):
                    dialog = EditGameDialog(self.jobs[row], self.available_bases, self)
                    if dialog.exec_():
                        # 편집 다이얼로그에서 저장 후 테이블 업데이트
                        # Column 0: Update game title in the combined widget
                        title_widget = self.table.cellWidget(row, 0)
                        if title_widget:
                            title_label = title_widget.layout().itemAt(0).widget()
                            title_label.setText(self.jobs[row].title_name)

                        # Update image previews if changed
                        self.update_icon_preview(row, self.jobs[row])
                return

    def edit_game_by_row(self, row):
        """Edit game by row index."""
        self.edit_game(row, 0)

    def remove_selected(self):
        """Remove selected rows."""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        for row in sorted(selected_rows, reverse=True):
            if row < len(self.jobs):
                del self.jobs[row]
            self.table.removeRow(row)

        self.update_ui_state()

    def clear_all(self):
        """Clear all jobs."""
        if tr.current_language == "ko":
            title = "전체 삭제"
            msg = "목록에서 모든 게임을 제거하시겠습니까?"
        else:
            title = "Clear All"
            msg = "Remove all games from the list?"

        reply = show_message(self, "question", title, msg)

        if reply == QMessageBox.Yes:
            self.jobs.clear()
            self.table.setRowCount(0)
            self.update_ui_state()

    def update_ui_state(self):
        """Update UI state based on jobs."""
        has_jobs = len(self.jobs) > 0
        self.build_btn.setEnabled(has_jobs)
        if tr.current_language == "ko":
            self.status_label.setText(f"준비 완료 - {len(self.jobs)}개 게임 대기 중")
        else:
            self.status_label.setText(f"Ready - {len(self.jobs)} game(s) in queue")

    def start_batch_build(self):
        """Start batch building."""
        # Get keys from settings
        import json
        settings_file = Path.home() / ".wiivc_injector_settings.json"

        # If settings don't exist, show dialog to enter keys
        if not settings_file.exists():
            dialog = SimpleKeysDialog(self)
            if dialog.exec_() != QDialog.Accepted:
                return

        # Load settings
        try:
            print(f"[DEBUG] Loading settings from: {settings_file}")
            print(f"[DEBUG] File exists: {settings_file.exists()}")

            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                print(f"[DEBUG] Settings loaded: {settings}")

                common_key = settings.get('wii_u_common_key', '')
                title_key_rhythm = settings.get('title_key_rhythm_heaven', '')
                title_key_xenoblade = settings.get('title_key_xenoblade', '')
                title_key_galaxy = settings.get('title_key_galaxy2', '')

                print(f"[DEBUG] Common key: {'SET' if common_key else 'NOT SET'}")
                print(f"[DEBUG] Rhythm key: {'SET' if title_key_rhythm else 'NOT SET'}")

                if not common_key or not title_key_rhythm:
                    msg = "Wii U Common Key와 Rhythm Heaven 키가 필요합니다!" if tr.current_language == "ko" else "Wii U Common Key and Rhythm Heaven key are required!"
                    show_message(self, "warning", tr.get("error"), msg)
                    return

                # Use Rhythm Heaven as fallback if others are missing
                if not title_key_xenoblade:
                    title_key_xenoblade = title_key_rhythm
                if not title_key_galaxy:
                    title_key_galaxy = title_key_rhythm
        except Exception as e:
            import traceback
            traceback.print_exc()
            msg = f"설정 로드 실패: {e}" if tr.current_language == "ko" else f"Failed to load settings: {e}"
            show_message(self, "warning", tr.get("error"), msg)
            return

        # Get output directory from settings or use default
        settings_file = Path.home() / ".wiivc_injector_settings.json"
        output_dir = None

        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    output_dir = settings.get('output_directory', '').strip()
            except:
                pass

        # If no output directory in settings, use first game's directory
        if not output_dir:
            if self.jobs:
                first_game_path = self.jobs[0].game_path
                output_dir = str(first_game_path.parent)
                print(f"No output directory in settings, using game directory: {output_dir}")
            else:
                # Should not happen, but fallback to dialog
                dialog_title = "출력 디렉토리 선택" if tr.current_language == "ko" else "Select Output Directory"
                output_dir = QFileDialog.getExistingDirectory(self, dialog_title)
                if not output_dir:
                    return

        # Prepare all metadata in main thread (to avoid SQLite threading issues)
        for job in self.jobs:
            if not job.title_name or not job.title_id:
                self.prepare_job_metadata(job)

        # Disable controls
        self.build_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Start batch builder
        title_keys = {
            'Rhythm Heaven Fever (USA)': title_key_rhythm,
            'Xenoblade Chronicles (USA)': title_key_xenoblade,
            'Super Mario Galaxy 2 (EUR)': title_key_galaxy
        }

        # Store available bases (only those with valid title keys)
        self.available_bases = {
            name: key for name, key in title_keys.items() if key
        }

        self.batch_builder = BatchBuilder(
            self.jobs,
            common_key,
            title_keys,
            Path(output_dir),
            self.auto_icons_check.isChecked(),
            keep_temp_for_debug=self.keep_temp_check.isChecked()
        )

        self.batch_builder.progress_updated.connect(self.on_progress)
        self.batch_builder.job_started.connect(self.on_job_started)
        self.batch_builder.job_finished.connect(self.on_job_finished)
        self.batch_builder.all_finished.connect(self.on_all_finished)

        # Disable UI during build
        self.set_ui_enabled(False)

        self.batch_builder.start()

    def stop_build(self):
        """Stop batch build."""
        if self.batch_builder:
            self.batch_builder.stop()

    def on_progress(self, current, total, message):
        """Handle progress update."""
        # current is already a percentage (0-100) from batch_builder
        # total is always 100
        self.progress_bar.setValue(current)
        self.status_label.setText(message)

    def on_job_started(self, idx, game_name):
        """Handle job started."""
        if idx < self.table.rowCount():
            status_item = self.table.item(idx, 5)
            status_text = "빌드 중..." if tr.current_language == "ko" else "Building..."
            status_item.setText(status_text)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setBackground(QColor(173, 216, 230))  # Light blue

    def on_job_finished(self, idx, success, message):
        """Handle job finished."""
        if idx < self.table.rowCount():
            status_item = self.table.item(idx, 5)
            if success:
                status_text = "완료" if tr.current_language == "ko" else "Completed"
                status_item.setText(status_text)
                status_item.setTextAlignment(Qt.AlignCenter)
                status_item.setBackground(QColor(200, 230, 201))  # Green
            else:
                failed_text = "실패" if tr.current_language == "ko" else "Failed"
                status_item.setText(f"{failed_text}: {message}")
                status_item.setTextAlignment(Qt.AlignCenter)
                status_item.setBackground(QColor(255, 205, 210))  # Red

    def on_all_finished(self, success_count, total_count):
        """Handle all jobs finished."""
        # Re-enable UI after build
        self.set_ui_enabled(True)

        self.build_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)

        if tr.current_language == "ko":
            self.status_label.setText(f"완료: {success_count}/{total_count} 성공")
            title = "일괄 빌드 결과 안내"
            msg = f"일괄 빌드가 완료되었습니다!\n\n성공: {success_count}개\n실패: {total_count - success_count}개\n전체: {total_count}개"
        else:
            self.status_label.setText(f"Completed: {success_count}/{total_count} succeeded")
            title = "Batch Build Results"
            msg = f"Batch build completed!\n\nSuccess: {success_count}\nFailed: {total_count - success_count}\nTotal: {total_count}"

        show_message(self, "info", title, msg, min_width=500)

    def set_ui_enabled(self, enabled: bool):
        """Enable or disable UI elements during build."""
        # Disable/enable top buttons
        self.add_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
        self.compat_btn.setEnabled(enabled)
        self.settings_btn.setEnabled(enabled)
        self.auto_icons_check.setEnabled(enabled)

        # Disable/enable table editing (edit buttons and pad option comboboxes)
        self.table.setEnabled(enabled)

    def show_settings(self):
        """Show settings dialog for encryption keys."""
        dialog = SimpleKeysDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Reload available bases after settings change
            self.load_available_bases()

    def load_available_bases(self):
        """Load available bases from settings file."""
        import json
        from pathlib import Path

        settings_file = Path.home() / ".wiivc_injector_settings.json"
        if not settings_file.exists():
            return

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            title_keys = {
                'Rhythm Heaven Fever (USA)': settings.get('title_key_rhythm_heaven', ''),
                'Xenoblade Chronicles (USA)': settings.get('title_key_xenoblade', ''),
                'Super Mario Galaxy 2 (EUR)': settings.get('title_key_galaxy2', '')
            }

            # Store only bases with valid title keys
            self.available_bases = {
                name: key for name, key in title_keys.items() if key
            }

            print(f"[DEBUG] Loaded available bases: {list(self.available_bases.keys())}")

        except Exception as e:
            print(f"[WARN] Failed to load available bases: {e}")

    def show_compatibility_list(self):
        """Show compatibility list dialog."""
        dialog = CompatibilityListDialog(self)
        dialog.exec_()

    def on_pad_option_changed(self, row, index):
        """Handle pad option combobox change."""
        if row < len(self.jobs):
            job = self.jobs[row]
            # 7 Controller Profiles mapping
            # Index: 0=no_gamepad, 1=none(CC), 2=gamepad_lr, 3=wiimote, 4=horizontal_wiimote, 5=galaxy_allstars, 6=galaxy_nvidia
            if index == 0:
                job.pad_option = "no_gamepad"  # Profile 1: 미적용 (Wii 리모컨만)
            elif index == 1:
                job.pad_option = "none"  # Profile 2: 게임패드 CC
            elif index == 2:
                job.pad_option = "gamepad_lr"  # Profile 3: 게임패드 CC+LR
            elif index == 3:
                job.pad_option = "wiimote"  # Profile 4: 게임패드 위모트(세로)
            elif index == 4:
                job.pad_option = "horizontal_wiimote"  # Profile 5: 게임패드 위모트(가로)
            elif index == 5:
                job.pad_option = "galaxy_allstars"  # Profile 6: 갤럭시 올스타
            else:
                job.pad_option = "galaxy_nvidia"  # Profile 7: 갤럭시 엔비디아
            print(f"[INFO] Pad option for {job.title_name}: {job.pad_option}")

    def on_cell_clicked(self, row, column):
        """Handle cell click - allow manual icon/banner selection."""
        if row >= len(self.jobs):
            return

        job = self.jobs[row]

        # Column 1: Icon, Column 2: Banner
        if column == 1:  # Icon column
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "아이콘 이미지 선택" if tr.current_language == "ko" else "Select Icon Image",
                "",
                "Images (*.png *.jpg *.jpeg);;All Files (*.*)"
            )
            if file_path:
                from pathlib import Path
                icon_path = Path(file_path)
                job.icon_path = icon_path
                self.update_icon_preview(row, job)
                print(f"[INFO] Icon updated for {job.game_path.name}: {icon_path}")

        elif column == 2:  # Banner column
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "배너 이미지 선택" if tr.current_language == "ko" else "Select Banner Image",
                "",
                "Images (*.png *.jpg *.jpeg);;All Files (*.*)"
            )
            if file_path:
                from pathlib import Path
                banner_path = Path(file_path)
                job.banner_path = banner_path
                self.update_icon_preview(row, job)
                print(f"[INFO] Banner updated for {job.game_path.name}: {banner_path}")

