"""Batch build window - Simplified UI for mass injection."""
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QLabel, QCheckBox, QFileDialog, QMessageBox, QLineEdit, QDialog,
    QFormLayout, QStyle, QProgressDialog, QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QPixmap, QIcon, QFont, QBrush, QPalette
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
        # Use custom buttons with Korean text
        ok_text = "확인" if tr.current_language == "ko" else "OK"
        cancel_text = "취소" if tr.current_language == "ko" else "Cancel"
        ok_btn = msg_box.addButton(ok_text, QMessageBox.AcceptRole)
        cancel_btn = msg_box.addButton(cancel_text, QMessageBox.RejectRole)
        msg_box.exec_()
        if msg_box.clickedButton() == ok_btn:
            return QMessageBox.Yes
        else:
            return QMessageBox.No

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

            # Second pass: Download icons in parallel (multiple games at once)
            if self.auto_download_icons and jobs_to_process:
                with ThreadPoolExecutor(max_workers=8) as executor:
                    # Submit all download jobs
                    future_to_job = {}
                    for idx, job in jobs_to_process:
                        if self.should_stop:
                            break
                        future = executor.submit(self.download_icon_for_job, job)
                        future_to_job[future] = (idx, job)

                    # Process completed downloads as they finish
                    completed = 0
                    for future in as_completed(future_to_job):
                        if self.should_stop:
                            break

                        idx, job = future_to_job[future]
                        try:
                            future.result()  # Get result or raise exception
                        except Exception as e:
                            print(f"[ERROR] Download failed for {job.game_path.name}: {e}")

                        # Emit job after download completes
                        completed += 1
                        self.progress_updated.emit(completed, len(jobs_to_process))
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

        # Set title name - read both Korean and English titles from DB
        if found_game:
            # Get both titles from DB
            korean_title = found_game.get('korean_title', '')
            english_title = found_game.get('english_title', '')

            # Store both if available
            if korean_title:
                job.korean_title = korean_title
            if english_title:
                job.english_title = english_title

            # Set display title based on current language
            if tr.current_language == "ko" and korean_title:
                job.title_name = korean_title
                job.db_title = korean_title
                job.has_korean_title = True
            elif english_title:
                job.title_name = english_title
                job.db_title = english_title
                job.has_korean_title = bool(korean_title or english_title)
            elif korean_title:
                job.title_name = korean_title
                job.db_title = korean_title
                job.has_korean_title = True
            else:
                # No titles in DB, use original title
                db_title = found_game['title'].split('(')[0].strip() if found_game['title'] else game_title
                job.title_name = db_title
                job.db_title = db_title
                job.has_korean_title = False  # Will fetch from GameTDB later
        else:
            job.title_name = game_title
            job.db_title = game_title
            job.has_korean_title = False

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

        # WiiLink24 support check removed - requires NAND files to work anyway

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

        # Create SSL context early (needed for GameTDB title fetch)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

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

            # Check if we have cached titles
            cached_ko_file = cache_dir / "title_ko.txt"
            cached_en_file = cache_dir / "title_en.txt"

            ko_title = None
            en_title = None

            # Try to get Korean title from DB first
            if hasattr(job, 'has_korean_title') and job.has_korean_title:
                ko_title = job.title_name
                job.korean_title = ko_title
                print(f"  [DB] Using Korean title from DB: {ko_title}")

            # Try cached titles
            if not ko_title and cached_ko_file.exists():
                try:
                    ko_title = cached_ko_file.read_text(encoding='utf-8').strip()
                    if ko_title:
                        job.korean_title = ko_title
                        print(f"  [CACHE] Using cached Korean title: {ko_title}")
                except:
                    ko_title = None

            if cached_en_file.exists():
                try:
                    en_title = cached_en_file.read_text(encoding='utf-8').strip()
                    if en_title:
                        job.english_title = en_title
                        print(f"  [CACHE] Using cached English title: {en_title}")
                except:
                    en_title = None

            # If either title is missing, fetch from GameTDB
            if not ko_title or not en_title:
                print(f"  [FETCH] Missing titles (KO={bool(ko_title)}, EN={bool(en_title)}), fetching from GameTDB...")
                self.fetch_gametdb_title(job, game_id, ssl_context)
                # Update from fetched data
                if not ko_title:
                    ko_title = getattr(job, 'korean_title', None)
                if not en_title:
                    en_title = getattr(job, 'english_title', None)

            # Set display title based on language
            if ko_title:
                job.korean_title = ko_title
            if en_title:
                job.english_title = en_title

            if tr.current_language == "ko" and ko_title:
                job.title_name = ko_title
            elif en_title:
                job.title_name = en_title
            elif ko_title:
                job.title_name = ko_title

            # Save to cache and DB
            try:
                if ko_title:
                    (cache_dir / "title_ko.txt").write_text(ko_title, encoding='utf-8')
                if en_title:
                    (cache_dir / "title_en.txt").write_text(en_title, encoding='utf-8')
                if ko_title or en_title:
                    compatibility_db.update_titles(game_id, korean_title=ko_title, english_title=en_title)
            except:
                pass

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

                # Fetch title from GameTDB only if not already in DB
                if not (hasattr(job, 'has_korean_title') and job.has_korean_title):
                    self.fetch_gametdb_title(job, game_id, ssl_context)

                    # Save titles to cache and DB
                    try:
                        ko_title = getattr(job, 'korean_title', None)
                        en_title = getattr(job, 'english_title', None)

                        if ko_title:
                            (cache_dir / "title_ko.txt").write_text(ko_title, encoding='utf-8')
                        if en_title:
                            (cache_dir / "title_en.txt").write_text(en_title, encoding='utf-8')

                        # Update DB with both titles
                        compatibility_db.update_titles(game_id, korean_title=ko_title, english_title=en_title)
                    except:
                        pass

                return True

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

        # Try in priority order (region priority maintained)
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
                        headers={'User-Agent': 'Meta-Injector/1.0'}
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
                        headers={'User-Agent': 'Meta-Injector/1.0'}
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
                            headers={'User-Agent': 'Meta-Injector/1.0'}
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
                        headers={'User-Agent': 'Meta-Injector/1.0'}
                    )
                    with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
                        icon_data = response.read()
                        icon_path = cache_dir / "icon.png"
                        icon_path.write_bytes(icon_data)
                        job.icon_path = icon_path

                    # Download banner
                    req = urllib.request.Request(
                        banner_url,
                        headers={'User-Agent': 'Meta-Injector/1.0'}
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

                    # Try to get title from GameTDB only if not already in DB
                    if not (hasattr(job, 'has_korean_title') and job.has_korean_title):
                        self.fetch_gametdb_title(job, try_id, ssl_context)

                        # Save titles to cache and DB
                        try:
                            ko_title = getattr(job, 'korean_title', None)
                            en_title = getattr(job, 'english_title', None)

                            if ko_title:
                                (cache_dir / "title_ko.txt").write_text(ko_title, encoding='utf-8')
                            if en_title:
                                (cache_dir / "title_en.txt").write_text(en_title, encoding='utf-8')

                            # Update DB with both titles
                            compatibility_db.update_titles(try_id, korean_title=ko_title, english_title=en_title)
                        except:
                            pass

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

            # Save titles to cache (using DB title as fallback)
            try:
                ko_title = getattr(job, 'korean_title', None)
                en_title = getattr(job, 'english_title', None)

                if ko_title:
                    (cache_dir / "title_ko.txt").write_text(ko_title, encoding='utf-8')
                if en_title:
                    (cache_dir / "title_en.txt").write_text(en_title, encoding='utf-8')
            except:
                pass

        # Images are already saved to cache_dir during download, no need to copy again
        return True

    def fetch_gametdb_title(self, job: BatchBuildJob, game_id: str, ssl_context):
        """Fetch Korean title from GameTDB. Falls back to DB title if not found."""
        import urllib.request
        import re
        import time

        max_retries = 1
        for attempt in range(max_retries):
            try:
                # Add small delay between requests to avoid rate limiting
                if attempt > 0:
                    time.sleep(0.5)

                # GameTDB game page
                url = f"https://www.gametdb.com/Wii/{game_id}"
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'WiiVC-Injector/1.0'}
                )
                with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                    # Extract both Korean and English titles
                    ko_title = None
                    en_title = None

                    # Look for Korean title - pattern: title (KO)</td><td...>쿠킹 마마</td>
                    ko_match = re.search(r'title\s*\(KO\)</td><td[^>]*>([^<]+)</td>', html)
                    if ko_match:
                        ko_title = ko_match.group(1).strip()

                    # Look for EN title - pattern: title (EN)</td><td...>Cooking Mama</td>
                    en_match = re.search(r'title\s*\(EN\)</td><td[^>]*>([^<]+)</td>', html)
                    if en_match:
                        en_title = en_match.group(1).strip()

                    # Store both titles in job
                    if ko_title:
                        job.korean_title = ko_title
                        print(f"  [TITLE] GameTDB Korean: {ko_title}")
                    if en_title:
                        job.english_title = en_title
                        print(f"  [TITLE] GameTDB English: {en_title}")

                    # Set display title based on current language
                    if tr.current_language == "ko" and ko_title:
                        job.title_name = ko_title
                    elif en_title:
                        job.title_name = en_title
                    elif ko_title:
                        job.title_name = ko_title
                    else:
                        # No title found on GameTDB, keep DB title
                        print(f"  [TITLE] No GameTDB title, using DB: {job.title_name}")

                    return

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  [TITLE] GameTDB attempt {attempt + 1} failed, retrying...")
                    continue
                else:
                    # Keep DB title if all retries fail
                    db_title = getattr(job, 'db_title', job.title_name)
                    print(f"  [TITLE] GameTDB failed after {max_retries} attempts ({e}), using DB: {db_title}")
                    return


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
        settings_title = "설정" if tr.current_language == "ko" else "Settings"
        self.setWindowTitle(settings_title)
        self.setMinimumWidth(550)

        layout = QVBoxLayout(self)

        # Compatibility DB Update button (top left)
        top_layout = QHBoxLayout()
        db_update_text = "호환성 DB 업데이트" if tr.current_language == "ko" else "Update Compatibility DB"
        self.db_update_btn = QPushButton(db_update_text)
        self.db_update_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.db_update_btn.clicked.connect(self.update_compatibility_db)
        top_layout.addWidget(self.db_update_btn)
        top_layout.addStretch()
        # layout.addLayout(top_layout)

        # layout.addSpacing(10)

        # Form layout for aligned inputs
        form = QFormLayout()

        # Common Key (Required - highlighted)
        self.common_key_input = QLineEdit()
        self.common_key_input.setPlaceholderText(tr.get("common_key_placeholder"))
        self.common_key_input.setStyleSheet("QLineEdit { background-color: #fff8dc; border: 2px solid #ff6b6b; }")
        self.common_key_input.textChanged.connect(self.update_common_key_style)
        form.addRow("Wii U Common Key:", self.common_key_input)

        # Title Keys
        # Rhythm Heaven Fever (Required - highlighted)
        self.rhythm_key_input = QLineEdit()
        self.rhythm_key_input.setPlaceholderText("필수 - Rhythm Heaven Fever (USA)")
        self.rhythm_key_input.setStyleSheet("QLineEdit { background-color: #fff8dc; border: 2px solid #ff6b6b; }")
        self.rhythm_key_input.textChanged.connect(self.update_rhythm_key_style)
        form.addRow("Rhythm Heaven Fever:", self.rhythm_key_input)

        self.xenoblade_key_input = QLineEdit()
        self.xenoblade_key_input.setPlaceholderText("선택 - Xenoblade Chronicles (USA)")
        form.addRow("Xenoblade Chronicles:", self.xenoblade_key_input)

        self.galaxy_key_input = QLineEdit()
        self.galaxy_key_input.setPlaceholderText("선택 - Super Mario Galaxy 2 (EUR)")
        form.addRow("Mario Galaxy 2:", self.galaxy_key_input)

        # Output directory (in FormLayout with buttons)
        output_widget = QWidget()
        output_layout = QHBoxLayout(output_widget)
        output_layout.setContentsMargins(0, 0, 0, 0)

        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText(tr.get("output_folder_placeholder"))

        browse_btn = QPushButton(tr.get("browse"))
        browse_btn.clicked.connect(self.browse_output_dir)

        clear_btn = QPushButton(tr.get("clear"))
        clear_btn.clicked.connect(self.clear_output_dir)

        output_layout.addWidget(self.output_dir_input, 1)
        output_layout.addWidget(browse_btn)
        output_layout.addWidget(clear_btn)

        form.addRow(tr.get("output_folder"), output_widget)

        layout.addLayout(form)

        # Info box with improved design
        layout.addSpacing(15)
        if tr.current_language == "ko":
            info_text = "<b>참고:</b> Rhythm Heaven 키는 필수입니다. 나머지는 선택사항이며 없으면 Rhythm Heaven으로 빌드됩니다."
        else:
            info_text = "<b>Note:</b> Rhythm Heaven key is required. Others are optional, will fallback to Rhythm Heaven if not set."

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border: 1px solid #90caf9;
                border-radius: 4px;
                padding: 10px;
                color: #1565c0;
                font-size: 11px;
            }
        """)
        layout.addWidget(info_label)

        # Buttons
        layout.addSpacing(15)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()  # Align buttons to the right

        save_btn = QPushButton(tr.get("save"))
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5cb85c, stop:1 #4cae4c);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 16px;
                border: 1px solid #3d8b3d;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6cc76c, stop:1 #5cb85c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a9d4a, stop:1 #3d8b3d);
            }
        """)

        cancel_btn = QPushButton(tr.get("cancel"))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b6b, stop:1 #ee5555);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 16px;
                border: 1px solid #dd4444;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff5555, stop:1 #ee3333);
                border-color: #cc2222;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ee3333, stop:1 #dd2222);
            }
        """)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _update_required_field_style(self, line_edit: QLineEdit):
        """
        Generic method to update the style of a required QLineEdit based on content.
        """
        if line_edit.text():
            line_edit.setStyleSheet("QLineEdit { background-color: #e6ffe6; border: 2px solid #66bb66; }")
        else:
            line_edit.setStyleSheet("QLineEdit { background-color: #fff8dc; border: 2px solid #ff6b6b; }")

    def update_common_key_style(self):
        """Updates the style for the Wii U Common key input."""
        self._update_required_field_style(self.common_key_input)

    def update_rhythm_key_style(self):
        """Updates the style for the Rhythm Heaven Fever key input."""
        self._update_required_field_style(self.rhythm_key_input)

    def browse_output_dir(self):
        """Browse for output directory."""
        dialog_title = tr.get("output_folder").replace(":", "")
        output_dir = QFileDialog.getExistingDirectory(self, dialog_title)
        if output_dir:
            self.output_dir_input.setText(output_dir)

    def clear_output_dir(self):
        """Clear output directory setting to use default."""
        self.output_dir_input.clear()

    def update_compatibility_db(self):
        """Update compatibility database from UWUVCI repository."""
        from PyQt5.QtCore import QThread, pyqtSignal
        import urllib.request
        import json as json_lib
        import time

        # Confirm with user
        if tr.current_language == "ko":
            msg = "UWUVCI-PRIME 리포지토리에서 최신 호환성 데이터를 다운로드합니다.\n\nGameTDB에서 게임 ID를 검색하므로 시간이 걸릴 수 있습니다.\n계속하시겠습니까?"
            title = "호환성 DB 업데이트"
        else:
            msg = "Download latest compatibility data from UWUVCI-PRIME repository.\n\nThis may take time as it searches game IDs from GameTDB.\nContinue?"
            title = "Update Compatibility DB"

        # Create styled message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowFlags(msg_box.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # Use custom buttons with Korean text
        ok_text = "확인" if tr.current_language == "ko" else "OK"
        cancel_text = "취소" if tr.current_language == "ko" else "Cancel"
        ok_btn = msg_box.addButton(ok_text, QMessageBox.AcceptRole)
        cancel_btn = msg_box.addButton(cancel_text, QMessageBox.RejectRole)
        msg_box.exec_()
        if msg_box.clickedButton() == ok_btn:
            reply = QMessageBox.Yes
        else:
            reply = QMessageBox.No
        if reply != QMessageBox.Yes:
            return

        # Disable button during update
        self.db_update_btn.setEnabled(False)
        self.db_update_btn.setText("업데이트 중..." if tr.current_language == "ko" else "Updating...")

        # Import the update function
        try:
            # Run import script
            import subprocess
            import sys

            script_path = Path(__file__).parent.parent / "import_uwuvci_compat.py"

            # Create progress dialog
            progress = QMessageBox(self)
            progress.setWindowTitle(title)
            progress.setText("다운로드 중..." if tr.current_language == "ko" else "Downloading...")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.setModal(True)
            progress.show()

            # Process events to show the dialog
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()

            # Run import script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            progress.close()

            # Re-enable button
            self.db_update_btn.setEnabled(True)
            db_update_text = "호환성 DB 업데이트" if tr.current_language == "ko" else "Update Compatibility DB"
            self.db_update_btn.setText(db_update_text)

            if result.returncode == 0:
                # Success
                if tr.current_language == "ko":
                    success_msg = "호환성 DB가 성공적으로 업데이트되었습니다!"
                else:
                    success_msg = "Compatibility DB updated successfully!"

                show_message(self, "info", title, success_msg)
            else:
                # Error
                error_msg = result.stderr if result.stderr else result.stdout
                if tr.current_language == "ko":
                    fail_msg = f"업데이트 실패:\n\n{error_msg}"
                else:
                    fail_msg = f"Update failed:\n\n{error_msg}"

                show_message(self, "warning", title, fail_msg)

        except Exception as e:
            # Re-enable button
            self.db_update_btn.setEnabled(True)
            db_update_text = "호환성 DB 업데이트" if tr.current_language == "ko" else "Update Compatibility DB"
            self.db_update_btn.setText(db_update_text)

            error_msg = f"업데이트 실패: {e}" if tr.current_language == "ko" else f"Update failed: {e}"
            show_message(self, "warning", title, error_msg)

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

        settings_file = Path.home() / ".meta_injector_settings.json"
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

        settings_file = Path.home() / ".meta_injector_settings.json"
        if not settings_file.exists():
            return

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

                # Fill in existing values and update styles
                common_key = settings.get('wii_u_common_key', '')
                if common_key:
                    self.common_key_input.setText(common_key)
                self.update_common_key_style()

                rhythm_key = settings.get('title_key_rhythm_heaven', '')
                if rhythm_key:
                    self.rhythm_key_input.setText(rhythm_key)
                self.update_rhythm_key_style()

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
        # Icon will be loaded after UI setup
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
        btn_layout.addStretch() # Align buttons to the right

        save_btn = QPushButton(tr.get("save"))
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5cb85c, stop:1 #4cae4c);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 12px; /* Consistent padding */
                border: 1px solid #3d8b3d;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6cc76c, stop:1 #5cb85c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a9d4a, stop:1 #3d8b3d);
            }
        """)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton(tr.get("cancel"))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b6b, stop:1 #ee5555);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 12px; /* Consistent padding */
                border: 1px solid #dd4444;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff5555, stop:1 #ee3333);
                border-color: #cc2222;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ee3333, stop:1 #dd2222);
            }
        """)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Load icon with badge overlays (after all widgets are set up)
        self.load_initial_icon()

    def load_initial_icon(self):
        """Load initial icon with badge overlays if needed."""
        if self.job.icon_path and self.job.icon_path.exists():
            print(f"[DEBUG] Loading icon from: {self.job.icon_path}")
            pixmap = QPixmap(str(self.job.icon_path))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(192, 192, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Add badge overlays (Galaxy, Gamepad)
                scaled_pixmap = self.add_badges_overlay_large(scaled_pixmap, self.job)

                self.icon_preview.setPixmap(scaled_pixmap)
            else:
                print(f"[ERROR] Failed to load icon pixmap from: {self.job.icon_path}")
                no_image_text = "이미지 로드 실패" if tr.current_language == "ko" else "Failed to load image"
                self.icon_preview.setText(no_image_text)
        else:
            print(f"[DEBUG] Icon path not found or doesn't exist: {self.job.icon_path}")
            no_image_text = "이미지 없음\n클릭하여 선택" if tr.current_language == "ko" else "No Image\nClick to select"
            self.icon_preview.setText(no_image_text)

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
            self.job.icon_edited = True  # Mark as user-edited to force reprocessing
            print(f"[USER EDIT] Icon changed to: {file_path}")
            # Update icon preview
            self.load_initial_icon()

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
            self.job.banner_edited = True  # Mark as user-edited to force reprocessing
            print(f"[USER EDIT] Banner changed to: {file_path}")
            pixmap = QPixmap(file_path)
            self.banner_preview.setPixmap(pixmap.scaled(384, 216, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def add_badges_overlay_large(self, pixmap: QPixmap, job: BatchBuildJob) -> QPixmap:
        """Add badge overlays to larger pixmap (for edit dialog - 192x192)."""
        from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
        from PyQt5.QtCore import Qt, QRectF

        # Create a copy to draw on
        result = QPixmap(pixmap)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)

        font = QFont()
        font.setPixelSize(10)
        font.setBold(True)

        # Galaxy patch badge (bottom-right)
        pad_option = job.pad_option or ""
        if "allstars" in pad_option or "nvidia" in pad_option:
            badge_width = 50
            badge_height = 16
            badge_x = result.width() - badge_width - 6
            badge_y = result.height() - badge_height - 6

            if "allstars" in pad_option:
                color = QColor(255, 152, 0, 220)  # Orange
                text = "GALA"
            else:  # nvidia
                color = QColor(118, 185, 0, 220)  # Green
                text = "GALN"

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            badge_rect = QRectF(badge_x, badge_y, badge_width, badge_height)
            painter.drawRoundedRect(badge_rect, 3, 3)

            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(font)
            painter.drawText(badge_rect, Qt.AlignCenter, text)

        # CC patch badge (bottom-right) - gray for GCT patches
        elif job.pad_option == "cc_patch" or (job.pad_option and job.pad_option.startswith("gct_")):
            badge_width = 40
            badge_height = 16
            badge_x = result.width() - badge_width - 6
            badge_y = result.height() - badge_height - 6

            color = QColor(100, 100, 100, 220)  # Dark Gray
            text = "GCT"

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            badge_rect = QRectF(badge_x, badge_y, badge_width, badge_height)
            painter.drawRoundedRect(badge_rect, 3, 3)

            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(font)
            painter.drawText(badge_rect, Qt.AlignCenter, text)

        # Gamepad support badge (top-left)
        if job.pad_option in ["none", "force_cc", "gamepad_lr"]:
            badge_width = 40
            badge_height = 16
            badge_x = 6
            badge_y = 6

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(76, 175, 80, 220)))  # Green
            badge_rect = QRectF(badge_x, badge_y, badge_width, badge_height)
            painter.drawRoundedRect(badge_rect, 3, 3)

            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(font)
            # GP=자연, GP!=강제, GP+=강제+LR
            if job.pad_option == "none":
                text = "GP"
            elif job.pad_option == "force_cc":
                text = "GP!"
            else:
                text = "GP+"
            painter.drawText(badge_rect, Qt.AlignCenter, text)

        painter.end()
        return result

    def save(self):
        """Save changes."""
        self.job.title_name = self.title_input.text()
        # Title ID is read-only, don't save it
        # self.job.title_id = self.id_input.text()

        # Save selected base ROM if combo box exists
        if self.base_combo:
            self.job.host_game = self.base_combo.currentText()

        self.accept()


class GamepadHelpDialog(QDialog):
    """Dialog to show gamepad mapping images with left/right navigation."""

    def __init__(self, parent=None, initial_index=0, single_image_mode=False):
        super().__init__(parent)
        # Remove ? button from title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.current_index = 0
        self.initial_index = initial_index
        self.single_image_mode = single_image_mode  # If True, show only one image without navigation
        self.images = []
        self.init_ui()
        self.load_images()

    def init_ui(self):
        """Initialize UI."""
        title = "컨트롤러 매핑 안내" if tr.current_language == "ko" else "Controller Mapping"
        self.setWindowTitle(title)
        self.resize(550, 400)  # Compact size

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Image display area with navigation
        image_layout = QHBoxLayout()
        image_layout.setSpacing(4)

        # Left arrow button
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 30px;
                max-width: 30px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #ccc;
            }
        """)
        self.prev_btn.clicked.connect(self.prev_image)
        if not self.single_image_mode:
            image_layout.addWidget(self.prev_btn)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: white; border: 1px solid #ddd;")
        self.image_label.setScaledContents(False)
        image_layout.addWidget(self.image_label, 1)

        # Right arrow button
        self.next_btn = QPushButton("▶")
        self.next_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 30px;
                max-width: 30px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #ccc;
            }
        """)
        self.next_btn.clicked.connect(self.next_image)
        if not self.single_image_mode:
            image_layout.addWidget(self.next_btn)

        layout.addLayout(image_layout)

        # Page indicator
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("font-size: 11px; color: #666; padding: 3px;")
        if not self.single_image_mode:
            layout.addWidget(self.page_label)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch() # Push button to the right

        close_btn = QPushButton(tr.get("close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b6b, stop:1 #ee5555);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 12px; /* Consistent padding */
                border: 1px solid #dd4444;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff5555, stop:1 #ee3333);
                border-color: #cc2222;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ee3333, stop:1 #dd2222);
            }
        """)
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)

    def load_images(self):
        """Load gamepad mapping images."""
        from .resources import resources
        images_dir = resources.resources_dir / "images"

        # Load images in order
        image_files = [
            ("gamepad_allstar_mapping.jpg", "Galaxy AllStars 매핑" if tr.current_language == "ko" else "Galaxy AllStars Mapping"),
            ("gamepad_nvidia_mapping.jpg", "Galaxy Nvidia 매핑" if tr.current_language == "ko" else "Galaxy Nvidia Mapping"),
        ]

        if self.single_image_mode:
            # Load only the specified image
            if 0 <= self.initial_index < len(image_files):
                filename, title = image_files[self.initial_index]
                img_path = images_dir / filename
                if img_path.exists():
                    self.images.append((str(img_path), title))
        else:
            # Load all images
            for filename, title in image_files:
                img_path = images_dir / filename
                if img_path.exists():
                    self.images.append((str(img_path), title))

        if self.images:
            # Show initial image based on initial_index
            start_index = 0 if self.single_image_mode else min(self.initial_index, len(self.images) - 1)
            self.show_image(start_index)
        else:
            self.image_label.setText("이미지를 찾을 수 없습니다" if tr.current_language == "ko" else "Images not found")

    def show_image(self, index):
        """Display image at given index."""
        if 0 <= index < len(self.images):
            self.current_index = index
            img_path, title = self.images[index]

            # Load and display image
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                # Scale to fit window width (fill horizontally)
                scaled_pixmap = pixmap.scaled(
                    500, 330,  # Compact size to fit the dialog
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("이미지 로드 실패" if tr.current_language == "ko" else "Failed to load image")

            # Update page indicator
            page_text = f"{index + 1} / {len(self.images)}"
            self.page_label.setText(page_text)

            # Update button states
            self.prev_btn.setEnabled(index > 0)
            self.next_btn.setEnabled(index < len(self.images) - 1)

    def prev_image(self):
        """Show previous image."""
        if self.current_index > 0:
            self.show_image(self.current_index - 1)

    def next_image(self):
        """Show next image."""
        if self.current_index < len(self.images) - 1:
            self.show_image(self.current_index + 1)


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

        # Search and filter bar
        search_layout = QHBoxLayout()

        # Category filter (GameCube, NDS hidden - not supported yet)
        category_label = QLabel("카테고리:" if tr.current_language == "ko" else "Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "전체" if tr.current_language == "ko" else "All",
            "Wii"
        ])
        self.category_combo.currentTextChanged.connect(self.filter_table)
        search_layout.addWidget(category_label)
        search_layout.addWidget(self.category_combo)

        search_layout.addSpacing(15)

        # Region filter
        region_label = QLabel("지역:" if tr.current_language == "ko" else "Region:")
        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "전체" if tr.current_language == "ko" else "All",
            "USA", "EUR", "JPN", "KOR"
        ])
        self.region_combo.currentTextChanged.connect(self.filter_table)
        search_layout.addWidget(region_label)
        search_layout.addWidget(self.region_combo)

        search_layout.addSpacing(15)

        # Gamepad compatibility filter
        gamepad_label = QLabel("게임패드:" if tr.current_language == "ko" else "Gamepad:")
        self.gamepad_combo = QComboBox()
        if tr.current_language == "ko":
            self.gamepad_combo.addItems(["전체", "지원", "일부지원", "강제가능", "미지원", "알수없음"])
        else:
            self.gamepad_combo.addItems(["All", "Works", "Partial", "Force OK", "Doesn't Work", "Unknown"])
        self.gamepad_combo.currentTextChanged.connect(self.filter_table)
        search_layout.addWidget(gamepad_label)
        search_layout.addWidget(self.gamepad_combo)

        search_layout.addSpacing(15)

        # GCT patch filter
        self.gct_filter_checkbox = QCheckBox("GCT 패치" if tr.current_language == "ko" else "GCT Patch")
        self.gct_filter_checkbox.stateChanged.connect(self.filter_table)
        search_layout.addWidget(self.gct_filter_checkbox)

        search_layout.addSpacing(15)

        # Search box
        search_label = QLabel("검색:" if tr.current_language == "ko" else "Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("게임 이름 또는 ID..." if tr.current_language == "ko" else "Game name or ID...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)

        layout.addLayout(search_layout)

        # Simple styling - keep native combobox arrow
        self.category_combo.setMinimumWidth(80)
        self.region_combo.setMinimumWidth(70)
        self.gamepad_combo.setMinimumWidth(90)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # Added No. column
        if tr.current_language == "ko":
            headers = ["No.", "카테고리", "게임 ID", "게임 제목", "지역", "게임패드 호환", "GCT 패치", "호스트 게임"]
        else:
            headers = ["No.", "Category", "Game ID", "Game Title", "Region", "Gamepad Compat", "GCT Patch", "Host Game"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)  # Hide default row numbers
        self.table.setColumnWidth(0, 45)   # No.
        self.table.setColumnWidth(1, 80)   # Category
        self.table.setColumnWidth(2, 80)   # Game ID
        self.table.setColumnWidth(4, 60)   # Region
        self.table.setColumnWidth(5, 150)  # Gamepad Compat
        self.table.setColumnWidth(6, 90)   # GCT Patch
        self.table.setColumnWidth(7, 150)  # Host Game
        # Use stretch for title column only
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Game Title
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # Allow editing only game_id column (column 0)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.itemChanged.connect(self.on_item_changed)

        # Table styling - minimal to preserve cell background colors
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(False)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()

        # Result count label (left side)
        self.result_count_label = QLabel("")
        self.result_count_label.setStyleSheet("color: #333; font-size: 12px;")
        btn_layout.addWidget(self.result_count_label)

        btn_layout.addStretch() # Push buttons to the right

        save_btn = QPushButton("저장" if tr.current_language == "ko" else "Save")
        save_btn.clicked.connect(self.save_changes)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5cb85c, stop:1 #4cae4c);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 12px; /* Reduced horizontal padding */
                border: 1px solid #3d8b3d;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6cc76c, stop:1 #5cb85c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a9d4a, stop:1 #3d8b3d);
            }
        """)
        btn_layout.addWidget(save_btn)

        close_btn = QPushButton(tr.get("close") if tr.current_language == "ko" else "Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b6b, stop:1 #ee5555);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 12px; /* Reduced horizontal padding */
                border: 1px solid #dd4444;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff5555, stop:1 #ee3333);
                border-color: #cc2222;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ee3333, stop:1 #dd2222);
            }
        """)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        self.changes = {}  # Track changes: {(title, region): new_game_id}

    def load_data(self):
        """Load data from compatibility database."""
        from .cc_patch_manager import get_cc_patch_manager
        patch_manager = get_cc_patch_manager()

        games = compatibility_db.get_all_games()
        self.all_games = games

        self.table.setRowCount(len(games))
        for row, game in enumerate(games):
            # No. (column 0) - will be updated by filter_table
            no_item = QTableWidgetItem(str(row + 1))
            no_item.setTextAlignment(Qt.AlignCenter)
            no_item.setFlags(no_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, no_item)

            # Category (column 1)
            category = game.get('category', 'Wii')
            self.table.setItem(row, 1, QTableWidgetItem(category))

            # Game ID (column 2)
            game_id = game.get('game_id', '')
            self.table.setItem(row, 2, QTableWidgetItem(game_id))

            # Title (column 3)
            self.table.setItem(row, 3, QTableWidgetItem(game.get('title', '')))

            # Region (column 4)
            self.table.setItem(row, 4, QTableWidgetItem(game.get('region', '')))

            # GCT Patch availability (column 6) - check first for gamepad color
            patches = patch_manager.get_available_patches(game_id) if game_id else []
            has_patch = len(patches) > 0
            if patches:
                patch_types = [p['patch_type'] for p in patches]
                has_galaxy = 'allstars' in patch_types or 'nvidia' in patch_types
                has_cc = 'cc' in patch_types

                if has_galaxy and has_cc:
                    patch_text = "Galaxy+CC"
                    patch_item = QTableWidgetItem(patch_text)
                    patch_item.setBackground(QBrush(QColor(180, 255, 180)))  # Green
                elif has_galaxy:
                    patch_text = "Galaxy"
                    patch_item = QTableWidgetItem(patch_text)
                    patch_item.setBackground(QBrush(QColor(180, 220, 255)))  # Blue
                else:
                    patch_text = "CC"
                    patch_item = QTableWidgetItem(patch_text)
                    patch_item.setBackground(QBrush(QColor(255, 255, 180)))  # Yellow
            else:
                patch_item = QTableWidgetItem("-")
                patch_item.setForeground(QColor(180, 180, 180))
            patch_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, patch_item)

            # Gamepad compatibility with color (column 5) - considers patch availability
            gamepad = game.get('gamepad_compatibility') or 'Unknown'
            gamepad_lower = gamepad.lower()
            gamepad_item = QTableWidgetItem(gamepad)

            if 'works' in gamepad_lower and 'doesn\'t' not in gamepad_lower and 'partial' not in gamepad_lower:
                # Works - Green
                gamepad_item.setBackground(QBrush(QColor(180, 255, 180)))
            elif 'partial' in gamepad_lower:
                # Partially works - Yellow
                gamepad_item.setBackground(QBrush(QColor(255, 255, 180)))
            elif 'doesn\'t' in gamepad_lower:
                if has_patch:
                    # Doesn't work but has patch - Light blue (can force)
                    gamepad_item.setBackground(QBrush(QColor(180, 220, 255)))
                else:
                    # Doesn't work and no patch - Light red
                    gamepad_item.setBackground(QBrush(QColor(255, 180, 180)))
            elif 'unknown' in gamepad_lower:
                # Unknown - Gray
                gamepad_item.setBackground(QBrush(QColor(210, 210, 210)))
            else:
                # Other/Issues - Light orange
                gamepad_item.setBackground(QBrush(QColor(255, 210, 170)))
            self.table.setItem(row, 5, gamepad_item)

            # Host game (column 7)
            self.table.setItem(row, 7, QTableWidgetItem(game.get('host_game', '')))

        # Update initial count
        self.filter_table()

    def on_item_changed(self, item):
        """Track changes to game_id or title column."""
        row = item.row()
        if item.column() == 2:  # game_id column
            title_item = self.table.item(row, 3)
            region_item = self.table.item(row, 4)
            if title_item and region_item:
                # Use original title from all_games
                orig_title = self.all_games[row]['title']
                region = region_item.text()
                key = ('game_id', orig_title, region)
                self.changes[key] = item.text()
        elif item.column() == 3:  # title column
            region_item = self.table.item(row, 4)
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

    def filter_table(self, text=None):
        """Filter table by category, region, gamepad, GCT patch, and search text."""
        search_text = self.search_input.text().lower()
        selected_category = self.category_combo.currentText()
        selected_region = self.region_combo.currentText()
        selected_gamepad = self.gamepad_combo.currentText()
        gct_filter_enabled = self.gct_filter_checkbox.isChecked()

        for row in range(self.table.rowCount()):
            # Get values from columns (shifted by 1 due to No. column)
            category = self.table.item(row, 1).text() if self.table.item(row, 1) else "Wii"
            region = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
            gamepad = self.table.item(row, 5).text().lower() if self.table.item(row, 5) else ""
            patch_item = self.table.item(row, 6)

            # Filter by category
            if selected_category not in ["전체", "All"] and category != selected_category:
                self.table.setRowHidden(row, True)
                continue

            # Filter by region (JAP and JPN are treated the same)
            if selected_region not in ["전체", "All"]:
                if selected_region == "JPN":
                    if region not in ["JPN", "JAP"]:
                        self.table.setRowHidden(row, True)
                        continue
                elif region != selected_region:
                    self.table.setRowHidden(row, True)
                    continue

            # Filter by gamepad compatibility
            if selected_gamepad not in ["전체", "All"]:
                patch_text = patch_item.text() if patch_item else "-"
                has_patch = patch_text != "-"

                if selected_gamepad in ["지원", "Works"]:
                    # Works (not partially, not doesn't)
                    if "works" not in gamepad or "doesn't" in gamepad or "partial" in gamepad:
                        self.table.setRowHidden(row, True)
                        continue
                elif selected_gamepad in ["일부지원", "Partial"]:
                    # Partially works
                    if "partial" not in gamepad:
                        self.table.setRowHidden(row, True)
                        continue
                elif selected_gamepad in ["강제가능", "Force OK"]:
                    # Has GCT patch (can force gamepad support)
                    if not has_patch:
                        self.table.setRowHidden(row, True)
                        continue
                elif selected_gamepad in ["미지원", "Doesn't Work"]:
                    # Doesn't work and no patch
                    if not ("doesn't" in gamepad and not has_patch):
                        self.table.setRowHidden(row, True)
                        continue
                elif selected_gamepad in ["알수없음", "Unknown"]:
                    if "unknown" not in gamepad:
                        self.table.setRowHidden(row, True)
                        continue

            # Filter by GCT patch availability (column 6)
            if gct_filter_enabled:
                if not patch_item or patch_item.text() == "-":
                    self.table.setRowHidden(row, True)
                    continue

            # Filter by search text
            if search_text:
                match = False
                for col in range(1, self.table.columnCount()):  # Skip No. column
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                self.table.setRowHidden(row, not match)
            else:
                self.table.setRowHidden(row, False)

        # Update No. column with sequential numbers for visible rows
        visible_num = 0
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                visible_num += 1
                no_item = self.table.item(row, 0)
                if no_item:
                    no_item.setText(str(visible_num))

        # Update result count
        visible_count = visible_num
        total_count = self.table.rowCount()
        if tr.current_language == "ko":
            self.result_count_label.setText(f"결과: {visible_count}/{total_count}")
        else:
            self.result_count_label.setText(f"Results: {visible_count}/{total_count}")


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
        self.setWindowTitle(tr.get("app_title") + ("" if tr.current_language == "ko" else " - Batch Mode"))
        self.setGeometry(100, 100, 800, 500)  # 타이틀 ID 컬럼 제거로 너비 복원

        # Set window icon
        import sys
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            icon_path = Path(sys._MEIPASS) / "resources" / "images" / "icon.png"
        else:
            # Running as script
            icon_path = Path(__file__).parent.parent / "resources" / "images" / "icon.png"

        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            print(f"[WARN] Icon not found at: {icon_path}")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Top controls
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        # Modern button style with icon spacing
        btn_style = """
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ddd;
                padding: 8px 16px 8px 12px;
                border-radius: 6px;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #bbb;
            }
            QPushButton:pressed {
                background-color: #ddd;
            }
            QPushButton[interactive="false"] {
                background-color: #f0f0f0;
                color: #aaa;
                border-color: #e0e0e0;
            }
        """

        # Add Files button
        self.add_btn = QPushButton("  " + tr.get("add_files"))  # Add spacing before text
        self.add_btn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.add_btn.setStyleSheet(btn_style)
        self.add_btn.clicked.connect(self.add_games)
        top_layout.addWidget(self.add_btn)

        # Remove Selected button
        self.remove_btn = QPushButton("  " + tr.get("remove_selected"))  # Add spacing
        self.remove_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserStop))
        self.remove_btn.setStyleSheet(btn_style)
        self.remove_btn.clicked.connect(self.remove_selected)
        top_layout.addWidget(self.remove_btn)

        # Clear All button
        self.clear_btn = QPushButton("  " + tr.get("clear_all"))  # Add spacing
        self.clear_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.clear_btn.setStyleSheet(btn_style)
        self.clear_btn.clicked.connect(self.clear_all)
        top_layout.addWidget(self.clear_btn)

        # Compatibility list button
        compat_text = "호환성 목록" if tr.current_language == "ko" else "Compatibility"
        self.compat_btn = QPushButton("  " + compat_text)  # Add spacing
        self.compat_btn.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.compat_btn.setStyleSheet("""
            QPushButton {
                background-color: #E3F2FD; /* Very light blue background */
                color: #2196F3; /* Blue text */
                border: 1px solid #90CAF9; /* Light blue border */
                padding: 8px 16px 8px 12px; /* Match other buttons */
                border-radius: 6px; /* Match other buttons */
                font-size: 13px; /* Match other buttons */
                text-align: left; /* Match other buttons */
            }
            QPushButton:hover {
                background-color: #BBDEFB; /* Slightly darker blue on hover */
                border-color: #64B5F6;
            }
            QPushButton:pressed {
                background-color: #90CAF9; /* Even darker on pressed */
                border-color: #42A5F5;
            }
        """)
        self.compat_btn.clicked.connect(self.show_compatibility_list)

        top_layout.addStretch()

        self.auto_icons_check = QCheckBox(tr.get("auto_download"))
        self.auto_icons_check.setChecked(True)
        top_layout.addWidget(self.auto_icons_check)

        keep_temp_text = "임시 파일 유지" if tr.current_language == "ko" else "Keep Temp Files"
        self.keep_temp_check = QCheckBox(keep_temp_text)
        self.keep_temp_check.setChecked(False) # Default to not keeping temp files
        top_layout.addWidget(self.keep_temp_check)
        self.keep_temp_check.setVisible(False)

        # Settings button (with gear icon)
        settings_text = "⚙  설정" if tr.current_language == "ko" else "⚙  Settings"
        self.settings_btn = QPushButton(settings_text)
        self.settings_btn.setStyleSheet(btn_style)
        self.settings_btn.clicked.connect(self.show_settings)
        top_layout.addWidget(self.settings_btn)

        layout.addLayout(top_layout)

        # Search filter
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍")
        search_label.setStyleSheet("font-size: 14px;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색 (게임명, ID)..." if tr.current_language == "ko" else "Search (title, ID)...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.filter_game_list)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table header with help button
        # Game list table (파일명/게임제목 통합, 게임 ID 별도 표시, 호환성/패드옵션 통합)
        self.table = QTableWidget()
        self.table.setColumnCount(6)

        if tr.current_language == "ko":
            headers = ["게임제목 [파일명]", "게임 ID", "아이콘", "배너", "호환성 및 게임패드", "작업"]
        else:
            headers = ["Game Title [Filename]", "Game ID", "Icon", "Banner", "Compatibility & Gamepad", "Actions"]

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
        # Table body styling - lighter gridlines with rounded corners
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e8e8e8;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #e8f4ff;
            }
        """)
        # Set column widths (파일명/게임제목 통합, 게임 ID 별도, 호환성/패드옵션 통합)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # File Name / Game Title
        # 첫 번째 헤더만 좌측 정렬
        header_item = self.table.horizontalHeaderItem(0)
        if header_item:
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setColumnWidth(1, 80)   # Game ID
        self.table.setColumnWidth(2, 58)   # Icon preview (52x52)
        self.table.setColumnWidth(3, 100)  # Banner preview (92x52, 16:9)
        self.table.setColumnWidth(4, 150)  # Compatibility / Pad Option
        self.table.setColumnWidth(5, 90)   # Actions
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)

        # Connect signals for button state updates
        self.table.selectionModel().selectionChanged.connect(self.update_main_buttons_state)
        self.table.itemChanged.connect(self.update_main_buttons_state) # Update if item data changes (e.g., editing)
        
        # Context menu for CC Patch selection
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.update_main_buttons_state() # Set initial state of buttons
        layout.addWidget(self.table)
    

        # Progress section with message and percentage labels
        ready_text = "준비 완료 - 게임을 추가하세요" if tr.current_language == "ko" else "Ready - Add games to start"

        # Container for progress bar and labels
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(12, 8, 12, 10)
        progress_layout.setSpacing(4)

        # Top row: message (left) and percentage (right)
        top_row = QWidget()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(4, 0, 4, 0)
        top_row_layout.setSpacing(8)

        # Message label (left-aligned, expandable)
        self.progress_message = QLabel(ready_text)
        self.progress_message.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 12px;
                background: transparent;
            }
        """)
        top_row_layout.addWidget(self.progress_message, 1)  # stretch factor 1

        # Percentage label (right-aligned, fixed width, hidden by default)
        self.progress_percentage = QLabel("")
        self.progress_percentage.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.progress_percentage.setStyleSheet("""
            QLabel {
                color: #555;
                font-size: 12px;
                font-weight: 600;
                background: transparent;
                min-width: 40px;
            }
        """)
        self.progress_percentage.setVisible(False)  # Hidden when idle
        top_row_layout.addWidget(self.progress_percentage, 0)  # no stretch

        # Progress bar (no text, just visual indicator)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # Hide built-in text
        self.progress_bar.setFixedHeight(8)  # Thin progress bar

        # Modern styling - subtle when idle, vibrant when active
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #e8e8e8;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #66BB6A);
                border-radius: 4px;
            }
        """)

        # Add to layout
        progress_layout.addWidget(top_row)
        progress_layout.addWidget(self.progress_bar)

        # Container styling - use objectName to target only the container
        progress_container.setObjectName("progressContainer")
        progress_container.setStyleSheet("""
            #progressContainer {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: #f8f8f8;
            }
        """)

        layout.addWidget(progress_container)

        # Bottom controls
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.compat_btn)
        bottom_layout.addStretch()

        build_text = "빌드" if tr.current_language == "ko" else "Build"
        self.build_btn = QPushButton(build_text)
        self.build_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb85c, stop:1 #4cae4c);
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 24px;
                border: 1px solid #3d8b3d;
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
                border: 1px solid #ccc;
            }
        """)
        self.build_btn.clicked.connect(self.start_batch_build)
        self.build_btn.setEnabled(False)
        bottom_layout.addWidget(self.build_btn)

        stop_text = "중지" if tr.current_language == "ko" else "Stop"
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

        # Allow duplicate files for multiple builds with different options
        new_file_paths = file_paths

        # Show loading status
        if tr.current_language == "ko":
            self.progress_message.setText(f"{len(new_file_paths)}개 게임 로딩 중...")
        else:
            self.progress_message.setText(f"Loading {len(new_file_paths)} games...")
        self.progress_percentage.setVisible(False)

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

    def show_context_menu(self, position):
        """Show context menu for game list options."""
        from PyQt5.QtWidgets import QMenu, QAction, QApplication

        # Get selected rows
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        menu = QMenu()

        # Style the menu - remove icon padding for cleaner look
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 6px 20px 6px 12px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #e8f4ff;
                color: #333;
            }
            QMenu::separator {
                height: 1px;
                background-color: #d0d0d0;
                margin: 4px 8px;
            }
        """)

        # Single selection actions
        if len(selected_rows) == 1:
            row = selected_rows[0].row()
            if row < len(self.jobs):
                job = self.jobs[row]

                # Build full title (Korean + English)
                ko_title = getattr(job, 'korean_title', '')
                en_title = getattr(job, 'english_title', '')
                if ko_title and en_title and ko_title != en_title:
                    full_title = f"{ko_title} ({en_title})"
                else:
                    full_title = ko_title or en_title or job.title_name

                # Copy Game ID
                copy_id_text = "게임 ID 복사" if tr.current_language == "ko" else "Copy Game ID"
                action_copy_id = QAction(copy_id_text, self)
                game_id = job.game_info.get('game_id', '')  # Capture value
                action_copy_id.triggered.connect(lambda checked, gid=game_id: QApplication.clipboard().setText(gid))
                menu.addAction(action_copy_id)

                # Copy Game Title
                copy_title_text = "게임 제목 복사" if tr.current_language == "ko" else "Copy Game Title"
                action_copy_title = QAction(copy_title_text, self)
                action_copy_title.triggered.connect(lambda checked, t=full_title: QApplication.clipboard().setText(t))
                menu.addAction(action_copy_title)

                # Open GameTDB
                if game_id:
                    gametdb_text = "GameTDB에서 보기" if tr.current_language == "ko" else "View on GameTDB"
                    action_gametdb = QAction(gametdb_text, self)
                    gametdb_url = f"https://www.gametdb.com/Wii/{game_id}"
                    action_gametdb.triggered.connect(lambda checked, url=gametdb_url: __import__('webbrowser').open(url))
                    menu.addAction(action_gametdb)

                menu.addSeparator()

                # Edit action
                edit_text = "편집" if tr.current_language == "ko" else "Edit"
                action_edit = QAction(edit_text, self)
                r = row  # Capture value
                action_edit.triggered.connect(lambda checked, r=r: self.edit_game_directly(r))
                menu.addAction(action_edit)

                # Retry action (only for failed jobs)
                if job.status == "failed":
                    retry_text = "재시도" if tr.current_language == "ko" else "Retry"
                    action_retry = QAction(retry_text, self)
                    action_retry.triggered.connect(lambda checked, r=r: self.retry_failed_job(r))
                    menu.addAction(action_retry)

                menu.addSeparator()

        # Retry all failed (for multiple selection or any selection with failed items)
        failed_rows = [idx.row() for idx in selected_rows if idx.row() < len(self.jobs) and self.jobs[idx.row()].status == "failed"]
        if failed_rows:
            retry_all_text = f"실패 항목 재시도 ({len(failed_rows)}개)" if tr.current_language == "ko" else f"Retry Failed ({len(failed_rows)})"
            action_retry_all = QAction(retry_all_text, self)
            action_retry_all.triggered.connect(lambda checked, rows=failed_rows: self.retry_failed_jobs(rows))
            menu.addAction(action_retry_all)
            menu.addSeparator()

        # Remove action
        remove_text = "제거" if tr.current_language == "ko" else "Remove"
        action_remove = QAction(remove_text, self)
        action_remove.triggered.connect(self.remove_selected)
        menu.addAction(action_remove)

        menu.exec_(self.table.viewport().mapToGlobal(position))

    def edit_game_directly(self, row):
        """Open edit dialog for a specific row."""
        if row < len(self.jobs):
            dialog = EditGameDialog(self.jobs[row], self.available_bases, self)
            if dialog.exec_():
                # Update table after edit
                title_widget = self.table.cellWidget(row, 0)
                if title_widget:
                    title_label = title_widget.layout().itemAt(0).widget()
                    title_label.setText(self.jobs[row].title_name)
                self.update_icon_preview(row, self.jobs[row])
        
    def set_cc_patch(self, rows, patch_info):
        """Set CC patch for selected jobs."""
        for index in rows:
            row = index.row()
            if row < len(self.jobs):
                job = self.jobs[row]
                
                if patch_info is None:
                    # Auto
                    if hasattr(job, 'selected_cc_patch'):
                        delattr(job, 'selected_cc_patch')
                    print(f"[Patch] Reset to Auto for {job.title_name}")
                elif patch_info == "none":
                    # Disable
                    job.selected_cc_patch = None
                    print(f"[Patch] Disabled for {job.title_name}")
                else:
                    # Specific Patch
                    job.selected_cc_patch = patch_info
                    print(f"[Patch] Set {patch_info['display_name']} for {job.title_name}")
                
                # Update UI to reflect change (Badge update needed? Maybe later)
                # For now just refresh the icon/badge
                self.update_icon_preview(row, job)

    def cancel_loading(self):
        """Cancel game loading."""
        if self.loader_thread:
            self.loader_thread.stop()
            if tr.current_language == "ko":
                self.progress_message.setText("로딩 취소됨")
            else:
                self.progress_message.setText("Loading canceled")
            self.progress_percentage.setVisible(False)

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
            self.progress_message.setText(f"{len(self.jobs)}개 게임 로드됨... (계속 로딩 중...)")
        else:
            self.progress_message.setText(f"Loaded {len(self.jobs)} games...")
        self.progress_percentage.setVisible(False)
        self.update_ui_state()

    def on_loading_finished(self, total_loaded):
        """Handle when all games are loaded."""
        # Close progress dialog
        if hasattr(self, 'loading_progress'):
            self.loading_progress.close()
            delattr(self, 'loading_progress')

        if tr.current_language == "ko":
            self.progress_message.setText(f"준비 완료 - {total_loaded}개 게임 로드됨")
        else:
            self.progress_message.setText(f"Ready - {total_loaded} games loaded")
        self.progress_percentage.setVisible(False)
        self.loader_thread = None
        self.update_ui_state()

    def add_badges_overlay(self, pixmap: QPixmap, job: BatchBuildJob) -> QPixmap:
        """Add badge overlays to pixmap (Galaxy patch, Gamepad) - for 50x50 table icons."""
        from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
        from PyQt5.QtCore import Qt, QRectF

        # Create a copy to draw on
        result = QPixmap(pixmap)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)

        font = QFont()
        font.setPixelSize(5)
        font.setBold(True)

        # Galaxy patch badge (bottom-right)
        pad_option = job.pad_option or ""
        if "allstars" in pad_option or "nvidia" in pad_option:
            badge_width = 22
            badge_height = 8
            badge_x = result.width() - badge_width - 1
            badge_y = result.height() - badge_height - 1

            # Different colors for different patches
            if "allstars" in pad_option:
                color = QColor(255, 152, 0, 200)  # Orange
                text = "GALA"
            else:  # nvidia
                color = QColor(118, 185, 0, 200)  # Green
                text = "GALN"

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            badge_rect = QRectF(badge_x, badge_y, badge_width, badge_height)
            painter.drawRoundedRect(badge_rect, 1.5, 1.5)

            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(font)
            painter.drawText(badge_rect, Qt.AlignCenter, text)

            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(font)
            painter.drawText(badge_rect, Qt.AlignCenter, text)

        # Forced Custom Patch Badge (Cyan) - overrides others
        elif hasattr(job, 'selected_cc_patch') and job.selected_cc_patch:
            badge_width = 22
            badge_height = 8
            badge_x = result.width() - badge_width - 1
            badge_y = result.height() - badge_height - 1 - 9 # Stack above if needed, or just replace
            # Actually easier to just replace the bottom right slot or stack it
            # Let's put it top-right for visibility? Or replace CC badge.
            # User likely won't mix Galaxy patch + Cursor patch, but just in case let's use bottom-right (priority)
            
            # Cyan color
            color = QColor(0, 188, 212, 220) 
            text = "PATCH"

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            badge_rect = QRectF(badge_x, badge_y, badge_width, badge_height)
            painter.drawRoundedRect(badge_rect, 1.5, 1.5)

            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(font)
            painter.drawText(badge_rect, Qt.AlignCenter, text)

        # CC patch badge (bottom-right) - gray for custom GCT patches
        elif job.pad_option == "cc_patch" or (job.pad_option and job.pad_option.startswith("gct_")):
            badge_width = 18
            badge_height = 8
            badge_x = result.width() - badge_width - 1
            badge_y = result.height() - badge_height - 1

            # Gray color for CC patches
            color = QColor(100, 100, 100, 220)  # Dark Gray
            text = "GCT"

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            badge_rect = QRectF(badge_x, badge_y, badge_width, badge_height)
            painter.drawRoundedRect(badge_rect, 1.5, 1.5)

            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(font)
            painter.drawText(badge_rect, Qt.AlignCenter, text)

        # Gamepad support badge (top-left)
        if job.pad_option in ["none", "force_cc", "gamepad_lr"]:
            badge_width = 18
            badge_height = 8
            badge_x = 1
            badge_y = 1

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(76, 175, 80, 200)))  # Green
            badge_rect = QRectF(badge_x, badge_y, badge_width, badge_height)
            painter.drawRoundedRect(badge_rect, 1.5, 1.5)

            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(font)
            # GP=자연, GP!=강제, GP+=강제+LR
            if job.pad_option == "none":
                text = "GP"
            elif job.pad_option == "force_cc":
                text = "GP!"
            else:
                text = "GP+"
            painter.drawText(badge_rect, Qt.AlignCenter, text)

        painter.end()
        return result

    def update_icon_preview(self, row: int, job: BatchBuildJob):
        """Update icon and banner preview in table."""
        # Update icon (Column 2) - Use QLabel for center alignment
        if job.icon_path and job.icon_path.exists():
            pixmap = QPixmap(str(job.icon_path))
            # Scale to 50x50 to fit better in 55px row height
            scaled_pixmap = pixmap.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Add badge overlays (Galaxy, Gamepad) - visual only, doesn't modify original
            scaled_pixmap = self.add_badges_overlay(scaled_pixmap, job)

            icon_label = QLabel()
            icon_label.setPixmap(scaled_pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("background: transparent;")
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
            # Scale to 89x50 to fit better in 55px row height (16:9 ratio)
            scaled_pixmap = pixmap.scaled(92, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            banner_label = QLabel()
            banner_label.setPixmap(scaled_pixmap)
            banner_label.setAlignment(Qt.AlignCenter)
            banner_label.setStyleSheet("background: transparent;")
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
        self.table.setRowHeight(row, 56)

        # Column 0: Game title / File name (Combined)
        title_widget = QWidget()
        title_widget.setAttribute(Qt.WA_TranslucentBackground)
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(4, 0, 4, 0)
        title_layout.setSpacing(0)
        title_label = QLabel(job.title_name)
        title_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #000; background: transparent;")
        title_layout.addWidget(title_label)
        filename_label = QLabel(job.game_path.name)
        filename_label.setStyleSheet("font-size: 11px; color: #666; background: transparent;")
        title_layout.addWidget(filename_label)
        self.table.setCellWidget(row, 0, title_widget)

        # Column 1: Game ID and Wiilink Status
        id_widget = QWidget()
        id_widget.setAttribute(Qt.WA_TranslucentBackground)
        id_layout = QVBoxLayout(id_widget)
        id_layout.setContentsMargins(2, 1, 2, 1)
        id_layout.setSpacing(1)
        id_layout.setAlignment(Qt.AlignCenter)
        game_id = job.game_info.get('game_id', '') if job.game_info else ''
        game_id_label = QLabel(game_id)
        game_id_label.setAlignment(Qt.AlignCenter)
        game_id_label.setStyleSheet("background: transparent;")
        id_layout.addWidget(game_id_label)
        self.table.setCellWidget(row, 1, id_widget)

        # Columns 2 & 3: Icon/Banner (placeholders, actual images set in update_icon_preview)
        for i in range(2, 4):
            item = QTableWidgetItem("")
            self.table.setItem(row, i, item)

        # Column 4: Compatibility / Pad Option
        compat_widget = QWidget()
        compat_widget.setAttribute(Qt.WA_TranslucentBackground)
        compat_layout = QVBoxLayout(compat_widget)
        compat_layout.setContentsMargins(4, 0, 4, 4)
        compat_layout.setSpacing(3)
        gamepad_compat = job.gamepad_compatibility or "Unknown"
        compat_label = QLabel(gamepad_compat)
        compat_label.setAlignment(Qt.AlignCenter)
        compat_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        compat_label.setFixedHeight(22)
        gamepad_lower = gamepad_compat.lower()
        if 'works' in gamepad_lower and 'doesn\'t' not in gamepad_lower:
            compat_label.setStyleSheet("background-color: #c8ffc8; font-size: 11px; padding: 1px 4px; border-radius: 3px; border: 1px solid #80c080;")
        elif 'classic' in gamepad_lower or 'lr' in gamepad_lower:
            compat_label.setStyleSheet("background-color: #ffffc8; font-size: 11px; padding: 1px 4px; border-radius: 3px; border: 1px solid #c0c080;")
        elif 'unknown' in gamepad_lower:
            compat_label.setStyleSheet("background-color: #dcdcdc; font-size: 11px; padding: 1px 4px; border-radius: 3px; border: 1px solid #a0a0a0;")
        else:
            compat_label.setStyleSheet("background-color: #ffc8c8; font-size: 11px; padding: 1px 4px; border-radius: 3px; border: 1px solid #c08080;")
        compat_layout.addWidget(compat_label)
        pad_combo = QComboBox()
        pad_combo.setStyleSheet("font-size: 11px;")
        pad_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pad_combo.setFixedHeight(22)
        
        # Base pad options (always available)
        if tr.current_language == "ko":
            base_options = ["미적용 (위모트)", "게임패드", "게임패드 (강제)", "게임패드 + LR (강제)", "게임패드 위모트(↕)", "게임패드 위모트(↔)"]
        else:
            base_options = ["No Pad (Wiimote)", "Gamepad", "Gamepad (Force)", "Gamepad + LR (Force)", "Pad Wiimote(↕)", "Pad Wiimote(↔)"]
        
        # Check for available GCT patches for this game
        game_id = job.game_info.get('game_id', '') if job.game_info else ''
        gct_options = []  # Will store (display_name, patch_type) tuples
        
        if game_id:
            from .cc_patch_manager import get_cc_patch_manager
            patch_manager = get_cc_patch_manager()
            available_patches = patch_manager.get_available_patches(game_id)
            
            for patch in available_patches:
                patch_type = patch['patch_type']
                display_name = patch['display_name']
                
                # Map patch types to UI display names
                if tr.current_language == "ko":
                    if patch_type == 'allstars':
                        gct_options.append(("갤럭시 패치(올스타)", "galaxy_allstars"))
                    elif patch_type == 'allstars_nodeflicker':
                        gct_options.append(("갤럭시 패치(올스타/디플리커X)", "galaxy_allstars_nodeflicker"))
                    elif patch_type == 'nvidia':
                        gct_options.append(("갤럭시 패치(엔비디아)", "galaxy_nvidia"))
                    elif patch_type == 'nvidia_nodeflicker':
                        gct_options.append(("갤럭시 패치(엔비디아/디플리커X)", "galaxy_nvidia_nodeflicker"))
                    elif patch_type == 'cc':
                        gct_options.append(("게임패드 패치", "cc_patch"))
                    else:
                        gct_options.append((f"GCT: {display_name}", f"gct_{patch_type}"))
                else:
                    if patch_type == 'allstars':
                        gct_options.append(("Galaxy Patch(AllStars)", "galaxy_allstars"))
                    elif patch_type == 'allstars_nodeflicker':
                        gct_options.append(("Galaxy Patch(AllStars/NoDeflicker)", "galaxy_allstars_nodeflicker"))
                    elif patch_type == 'nvidia':
                        gct_options.append(("Galaxy Patch(Nvidia)", "galaxy_nvidia"))
                    elif patch_type == 'nvidia_nodeflicker':
                        gct_options.append(("Galaxy Patch(Nvidia/NoDeflicker)", "galaxy_nvidia_nodeflicker"))
                    elif patch_type == 'cc':
                        gct_options.append(("Gamepad Patch", "cc_patch"))
                    else:
                        gct_options.append((f"GCT: {display_name}", f"gct_{patch_type}"))
        
        # Add base options to combobox
        pad_combo.addItems(base_options)

        # Color code the base options
        # Index 0: 미적용 (Gray)
        pad_combo.setItemData(0, QBrush(QColor(220, 220, 220)), Qt.BackgroundRole)
        # Index 1-5: General options (White/Default - no color change)

        # Add GCT patch options (if any) with separator
        if gct_options:
            pad_combo.insertSeparator(pad_combo.count())

        for display_name, patch_type in gct_options:
            pad_combo.addItem(display_name)
            # GCT patch options (Yellow)
            idx = pad_combo.count() - 1
            pad_combo.setItemData(idx, QBrush(QColor(255, 255, 180)), Qt.BackgroundRole)

        # Store GCT option count for style update
        gct_start_index = 7 if gct_options else -1

        # No custom styling - use native combobox appearance
        
        # Store available GCT options in job for later reference
        job.available_gct_patches = gct_options

        # Always start with "no_gamepad" - user must explicitly select controller option
        pad_combo.setCurrentIndex(0)
        job.pad_option = "no_gamepad"
        pad_combo.currentIndexChanged.connect(lambda idx, r=row: self.on_pad_option_changed(r, idx))
        compat_layout.addWidget(pad_combo)
        self.table.setCellWidget(row, 4, compat_widget)

        # Column 5: Actions (Status + Edit button)
        action_widget = QWidget()
        action_widget.setAttribute(Qt.WA_TranslucentBackground)
        action_layout = QVBoxLayout(action_widget)
        action_layout.setContentsMargins(4, 0, 4, 4)
        action_layout.setSpacing(3)
        status_text = "대기 중" if tr.current_language == "ko" else "Pending"
        status_label = QLabel(status_text)
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        status_label.setFixedHeight(22)
        status_label.setStyleSheet("background-color: #fff9c4; border: 1px solid #fbc02d; color: #8c6b00; font-size: 11px; padding: 2px 5px; border-radius: 3px;")
        action_layout.addWidget(status_label)
        edit_text = "편집" if tr.current_language == "ko" else "Edit"
        edit_btn = QPushButton(edit_text)
        edit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        edit_btn.setFixedHeight(22)
        edit_btn.setStyleSheet("QPushButton { background-color: #fafafa; color: #555; border: 1px solid #ddd; padding: 4px 12px; border-radius: 4px; font-size: 11px; } QPushButton:hover { background-color: #f0f0f0; color: #333; border-color: #bbb; } QPushButton:disabled { background-color: #f0f0f0; color: #aaa; border-color: #e0e0e0; }")
        edit_btn.clicked.connect(lambda checked, btn=edit_btn: self.edit_game_by_button(btn))
        action_layout.addWidget(edit_btn)
        self.table.setCellWidget(row, 5, action_widget)

        self.update_main_buttons_state() # Update button states after adding a job
        return row

    def edit_game(self, row, column):
        """Edit game metadata (사용 안 함 - 편집 버튼으로만 수정)."""
        # 더블클릭 편집 비활성화됨
        pass

    def edit_game_by_button(self, button):
        """Edit game by finding the button's row in the table."""
        # Find the row by iterating through all rows to find the button
        for row in range(self.table.rowCount()):
            # The button is inside a widget in column 5 now
            action_widget = self.table.cellWidget(row, 5)
            if action_widget and button in action_widget.findChildren(QPushButton):
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

    def filter_game_list(self, text):
        """Filter game list by search text."""
        search_text = text.lower().strip()
        for row in range(self.table.rowCount()):
            if not search_text:
                self.table.setRowHidden(row, False)
                continue

            # Get title from column 0 (title widget)
            title_widget = self.table.cellWidget(row, 0)
            title_text = ""
            if title_widget:
                title_label = title_widget.layout().itemAt(0).widget()
                if title_label:
                    title_text = title_label.text().lower()

            # Get game ID from column 1
            game_id_widget = self.table.cellWidget(row, 1)
            game_id_text = ""
            if game_id_widget:
                id_label = game_id_widget.layout().itemAt(0).widget()
                if id_label:
                    game_id_text = id_label.text().lower()

            # Show row if search text matches title or game ID
            match = search_text in title_text or search_text in game_id_text
            self.table.setRowHidden(row, not match)

    def remove_selected(self):
        """Remove selected rows."""
        if self.remove_btn.property("interactive") != "true":
            return

        selected_indexes = self.table.selectionModel().selectedRows()
        if not selected_indexes:
            return  # Nothing selected

        # Get unique row numbers and sort them in reverse
        selected_rows = sorted(set(index.row() for index in selected_indexes), reverse=True)

        for row in selected_rows:
            if row < len(self.jobs):
                del self.jobs[row]
            self.table.removeRow(row)

        self.update_ui_state()

    def clear_all(self):
        """Clear all jobs."""
        if self.clear_btn.property("interactive") != "true":
            return

        if tr.current_language == "ko":
            title = "전체 제거"
            msg = "목록에서 모든 게임을 제거하시겠습니까?"
        else:
            title = "Remove All"
            msg = "Remove all games from the list?"

        reply = show_message(self, "question", title, msg)

        if reply == QMessageBox.Yes:
            self.jobs.clear()
            self.table.setRowCount(0)
            self.update_main_buttons_state() # Update button states after clearing
            self.update_ui_state()

    def update_main_buttons_state(self):
        """
        Enables or disables the remove_btn based on whether there are selected items in the table,
        and the clear_btn based on whether there are any rows in the table.
        Also updates the cursor to indicate if the button is interactive.
        """
        has_selection = self.table.selectionModel().hasSelection()
        has_rows = self.table.rowCount() > 0

        # Store property for click handler checks
        self.remove_btn.setProperty("interactive", "true" if has_selection else "false")
        self.clear_btn.setProperty("interactive", "true" if has_rows else "false")

        # Get normal icons once
        normal_remove_icon = self.style().standardIcon(QStyle.SP_BrowserStop)
        normal_clear_icon = self.style().standardIcon(QStyle.SP_TrashIcon)

        # Base button style
        active_style = """
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ddd;
                padding: 8px 16px 8px 12px;
                border-radius: 6px;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #bbb;
            }
            QPushButton:pressed {
                background-color: #ddd;
            }
        """

        inactive_style = """
            QPushButton {
                background-color: #f0f0f0;
                color: #aaa;
                border: 1px solid #e0e0e0;
                padding: 8px 16px 8px 12px;
                border-radius: 6px;
                font-size: 13px;
                text-align: left;
            }
        """

        # Update remove button
        if has_selection:
            self.remove_btn.setCursor(Qt.ArrowCursor)
            self.remove_btn.setIcon(normal_remove_icon)
            self.remove_btn.setStyleSheet(active_style)
        else:
            pixmap = normal_remove_icon.pixmap(self.remove_btn.iconSize(), QIcon.Disabled)
            self.remove_btn.setIcon(QIcon(pixmap))
            self.remove_btn.setCursor(Qt.ForbiddenCursor)
            self.remove_btn.setStyleSheet(inactive_style)

        # Update clear button
        if has_rows:
            self.clear_btn.setCursor(Qt.ArrowCursor)
            self.clear_btn.setIcon(normal_clear_icon)
            self.clear_btn.setStyleSheet(active_style)
        else:
            pixmap = normal_clear_icon.pixmap(self.clear_btn.iconSize(), QIcon.Disabled)
            self.clear_btn.setIcon(QIcon(pixmap))
            self.clear_btn.setCursor(Qt.ForbiddenCursor)
            self.clear_btn.setStyleSheet(inactive_style)

    def update_ui_state(self):
        """Update UI state based on jobs."""
        has_jobs = len(self.jobs) > 0
        self.build_btn.setEnabled(has_jobs)
        if tr.current_language == "ko":
            self.progress_message.setText(f"준비 완료 - {len(self.jobs)}개 게임 대기 중")
        else:
            self.progress_message.setText(f"Ready - {len(self.jobs)} game(s) in queue")
        self.progress_percentage.setVisible(False)
        self.update_main_buttons_state() # Update main buttons state consistently

    def update_conflict_styling(self):
        """Update table styling to show conflicting items in red."""
        for idx, job in enumerate(self.jobs):
            if idx >= self.table.rowCount():
                continue

            action_widget = self.table.cellWidget(idx, 5)
            if not action_widget:
                continue

            status_label = action_widget.findChild(QLabel)
            if not status_label:
                continue

            if job.has_output_conflict:
                # Mark as conflict
                conflict_text = "중복 (스킵)" if tr.current_language == "ko" else "Duplicate (Skip)"
                status_label.setText(conflict_text)
                status_label.setStyleSheet(
                    "background-color: #ffcdd2; border: 1px solid #ef5350; "
                    "color: #c62828; font-size: 11px; padding: 2px 5px; "
                    "border-radius: 3px; font-weight: bold;"
                )

                # Make entire row slightly red
                for col in range(self.table.columnCount()):
                    item = self.table.item(idx, col)
                    if item:
                        item.setBackground(QColor(255, 235, 235))  # Light red background
            else:
                # Reset to pending status if no conflict
                if job.status == "pending" or job.status == "skipped":
                    status_text = "대기 중" if tr.current_language == "ko" else "Pending"
                    status_label.setText(status_text)
                    status_label.setStyleSheet(
                        "background-color: #fff9c4; border: 1px solid #fbc02d; "
                        "color: #8c6b00; font-size: 11px; padding: 2px 5px; "
                        "border-radius: 3px;"
                    )

                # Clear row background
                for col in range(self.table.columnCount()):
                    item = self.table.item(idx, col)
                    if item:
                        item.setBackground(QColor(255, 255, 255))  # White background

    def detect_output_conflicts(self):
        """
        Detect and mark jobs with conflicting output paths.
        Returns number of conflicts found.
        """
        # Prefix map from build_engine.py
        prefix_map = {
            "no_gamepad": "NOGP_",
            "none": "GP_",
            "force_cc": "GPFC_",
            "gamepad_lr": "GPLR_",
            "wiimote": "WM_",
            "horizontal_wiimote": "HWM_",
            "passthrough": "PT_",
            "galaxy_allstars": "GALA_",
            "galaxy_allstars_nodeflicker": "GALANF_",
            "galaxy_nvidia": "GALN_",
            "galaxy_nvidia_nodeflicker": "GALNNF_",
            "cc_patch": "GCTCC_"
        }

        # Track output paths: {output_key: [job_indices]}
        output_paths = {}

        for idx, job in enumerate(self.jobs):
            # Get game ID
            game_id = job.game_info.get('game_id', '') if job.game_info else ''
            if not game_id:
                continue

            # Calculate output path key (prefix + game_id)
            # gct_ prefixed patches use GCTCC_ prefix
            if job.pad_option and job.pad_option.startswith("gct_"):
                prefix = "GCTCC_"
            else:
                prefix = prefix_map.get(job.pad_option, "")
            output_key = f"{prefix}{game_id}"

            if output_key not in output_paths:
                output_paths[output_key] = []
            output_paths[output_key].append(idx)

        # Mark conflicts (keep first, mark rest as conflicts)
        conflict_count = 0
        for output_key, indices in output_paths.items():
            if len(indices) > 1:
                # First job is OK, rest are conflicts
                for idx in indices[1:]:
                    self.jobs[idx].has_output_conflict = True
                    conflict_count += 1
                    print(f"[CONFLICT] Job {idx} ({self.jobs[idx].title_name}) conflicts with output path: {output_key}")

        return conflict_count

    def start_batch_build(self):
        """Start batch building."""
        # Detect and mark output path conflicts
        conflict_count = self.detect_output_conflicts()
        if conflict_count > 0:
            # Update table to show conflicts
            self.update_conflict_styling()

            # Show warning to user
            if tr.current_language == "ko":
                msg = f"{conflict_count}개 항목이 중복으로 인해 건너뛰어집니다.\n\n중복된 게임+옵션 조합이 감지되었습니다.\n중복 항목은 빨간색으로 표시되며 빌드에서 제외됩니다."
                title = "중복 항목 감지"
            else:
                msg = f"{conflict_count} item(s) will be skipped due to duplicates.\n\nDuplicate game+option combinations detected.\nDuplicate items are marked in red and will be excluded from build."
                title = "Duplicates Detected"

            reply = show_message(self, "warning", title, msg)

        # Get keys from settings
        import json
        settings_file = Path.home() / ".meta_injector_settings.json"

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
        settings_file = Path.home() / ".meta_injector_settings.json"
        output_dir = None

        print(f"[DEBUG] Loading settings from: {settings_file}")

        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    output_dir = settings.get('output_directory', '').strip()
                    print(f"[DEBUG] Loaded output_directory from settings: '{output_dir}'")

                    # Validate the path if it exists
                    if output_dir:
                        try:
                            # Check if it's a valid path format
                            test_path = Path(output_dir)
                            print(f"[DEBUG] Validated as path: {test_path}")
                        except Exception as path_err:
                            print(f"[WARN] Invalid path format in settings: {path_err}")
                            output_dir = None  # Force use of default
            except Exception as e:
                print(f"[DEBUG] Failed to load settings: {e}")

        # If no output directory in settings, use default Documents folder
        if not output_dir:
            # Try Documents folder first
            default_output = Path.home() / "Documents" / "WiiVC Builds"

            # If Documents doesn't exist, fall back to Desktop or home directory
            if not (Path.home() / "Documents").exists():
                print(f"[WARN] Documents folder not found, trying Desktop")
                if (Path.home() / "Desktop").exists():
                    default_output = Path.home() / "Desktop" / "WiiVC Builds"
                else:
                    print(f"[WARN] Desktop folder not found, using home directory")
                    default_output = Path.home() / "WiiVC Builds"

            default_output.mkdir(parents=True, exist_ok=True)
            output_dir = str(default_output)
            print(f"[DEBUG] No output directory in settings, using default: {output_dir}")

        # Normalize and resolve the path to absolute form
        output_dir_path = Path(output_dir).resolve()
        output_dir = str(output_dir_path)
        print(f"[DEBUG] Final output_dir for build: {output_dir}")
        print(f"[DEBUG] Output dir exists: {output_dir_path.exists()}")

        # Prepare all metadata in main thread (to avoid SQLite threading issues)
        for job in self.jobs:
            if not job.title_name or not job.title_id:
                self.prepare_job_metadata(job)

        # Disable controls
        self.build_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Store output directory for later use (e.g., open folder button)
        self.current_output_dir = output_dir
        print(f"[DEBUG] Stored current_output_dir: {self.current_output_dir}")

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
            # Reset progress indicators immediately when user stops
            self.progress_bar.setValue(0)
            self.progress_percentage.setVisible(False)
            if tr.current_language == "ko":
                self.progress_message.setText("중단됨")
            else:
                self.progress_message.setText("Stopped")

    def on_progress(self, current, total, message):
        """Handle progress update."""
        # current is already a percentage (0-100) from batch_builder
        # total is always 100
        self.progress_bar.setValue(current)
        # Update message and percentage labels separately
        self.progress_message.setText(message)
        self.progress_percentage.setText(f"{current}%")
        self.progress_percentage.setVisible(True)  # Show percentage during build

    def on_job_started(self, idx, game_name):
        """Handle job started."""
        if idx < self.table.rowCount():
            action_widget = self.table.cellWidget(idx, 5)
            if action_widget: # Check if the widget exists
                status_label = action_widget.findChild(QLabel)
                if status_label: # Check if the status label exists within the widget
                    status_text = "빌드 중..." if tr.current_language == "ko" else "Building..."
                    status_label.setText(status_text)
                    status_label.setStyleSheet("background-color: #bbdefb; border: 1px solid #90caf9; color: #1e3a5f; font-size: 11px; padding: 2px 5px; border-radius: 3px;")

    def on_job_finished(self, idx, success, message):
        """Handle job finished."""
        if idx < self.table.rowCount():
            action_widget = self.table.cellWidget(idx, 5)
            if action_widget:
                status_label = action_widget.findChild(QLabel)
                if status_label:
                    if success:
                        status_text = "완료" if tr.current_language == "ko" else "Completed"
                        status_label.setText(status_text)
                        status_label.setStyleSheet("background-color: #c8e6c9; border: 1px solid #a5d6a7; color: #256029; font-size: 11px; padding: 2px 5px; border-radius: 3px;")
                    else:
                        failed_text = "실패" if tr.current_language == "ko" else "Failed"
                        status_label.setText(f"{failed_text}")
                        status_label.setToolTip(message) # Add full error to tooltip
                        status_label.setStyleSheet("background-color: #ffcdd2; border: 1px solid #ef9a9a; color: #b71c1c; font-size: 11px; padding: 2px 5px; border-radius: 3px;")

    def on_all_finished(self, success_count, total_count):
        """Handle all jobs finished."""
        # Re-enable UI after build
        self.set_ui_enabled(True)

        self.build_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)

        if tr.current_language == "ko":
            self.progress_message.setText(f"완료: {success_count}/{total_count} 성공")
            title = "일괄 빌드 결과 안내"
            msg = f"일괄 빌드가 완료되었습니다!\n\n성공: {success_count}개\n실패: {total_count - success_count}개\n전체: {total_count}개"
            open_folder_text = "폴더 열기"
            close_text = "닫기"
        else:
            self.progress_message.setText(f"Completed: {success_count}/{total_count} succeeded")
            title = "Batch Build Results"
            msg = f"Batch build completed!\n\nSuccess: {success_count}\nFailed: {total_count - success_count}\nTotal: {total_count}"
            open_folder_text = "Open Folder"
            close_text = "Close"

        # Show 100% completion
        self.progress_percentage.setText("100%")
        self.progress_percentage.setVisible(True)

        # Create custom message box with "Open Folder" button
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setMinimumWidth(500)
        msg_box.setWindowFlags(msg_box.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Add custom buttons
        open_folder_btn = msg_box.addButton(open_folder_text, QMessageBox.ActionRole)
        close_btn = msg_box.addButton(close_text, QMessageBox.RejectRole)

        msg_box.exec_()

        # Check which button was clicked
        if msg_box.clickedButton() == open_folder_btn:
            # Open output folder
            import subprocess
            import platform
            output_path = getattr(self, 'current_output_dir', None)

            print(f"[DEBUG] ========== Open Folder Clicked ==========")
            print(f"[DEBUG] current_output_dir value: {output_path}")
            print(f"[DEBUG] current_output_dir type: {type(output_path)}")

            if output_path:
                # Convert to Path object and resolve to absolute path
                output_path_obj = Path(output_path).resolve()
                print(f"[DEBUG] Resolved path: {output_path_obj}")
                print(f"[DEBUG] Path exists: {output_path_obj.exists()}")
                print(f"[DEBUG] Path is dir: {output_path_obj.is_dir() if output_path_obj.exists() else 'N/A'}")

                if not output_path_obj.exists():
                    print(f"[ERROR] Output path does not exist: {output_path_obj}")
                    error_msg = "출력 폴더를 찾을 수 없습니다" if tr.current_language == "ko" else "Output folder not found"
                    show_message(self, "warning", tr.get("error"), error_msg)
                else:
                    # Use absolute string path for explorer
                    abs_path_str = str(output_path_obj.absolute())
                    print(f"[DEBUG] Opening with explorer: {abs_path_str}")

                    if platform.system() == 'Windows':
                        # Use /select to open and highlight the folder
                        subprocess.run(['explorer', abs_path_str])
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', abs_path_str])
                    else:  # Linux
                        subprocess.run(['xdg-open', abs_path_str])

                    print(f"[DEBUG] Explorer command executed")
            else:
                print("[ERROR] No output_path set in self.current_output_dir!")
                error_msg = "출력 경로가 설정되지 않았습니다" if tr.current_language == "ko" else "Output path not set"
                show_message(self, "warning", tr.get("error"), error_msg)

        # Reset progress bar and percentage after dialog closes
        self.progress_bar.setValue(0)
        self.progress_percentage.setVisible(False)

    def retry_failed_job(self, row):
        """Retry a single failed job."""
        self.retry_failed_jobs([row])

    def retry_failed_jobs(self, rows):
        """Retry multiple failed jobs."""
        if not rows:
            return

        # Reset status for failed jobs
        jobs_to_retry = []
        for row in rows:
            if row < len(self.jobs):
                job = self.jobs[row]
                if job.status == "failed":
                    job.status = "pending"
                    job.error_message = ""
                    jobs_to_retry.append(job)

                    # Update status label in table
                    action_widget = self.table.cellWidget(row, 5)
                    if action_widget:
                        status_label = action_widget.findChild(QLabel)
                        if status_label:
                            status_text = "대기 중" if tr.current_language == "ko" else "Pending"
                            status_label.setText(status_text)
                            status_label.setToolTip("")
                            status_label.setStyleSheet("background-color: #fff9c4; border: 1px solid #fbc02d; color: #8c6b00; font-size: 11px; padding: 2px 5px; border-radius: 3px;")

        if not jobs_to_retry:
            return

        # Start build for retry jobs only
        self.start_build_for_jobs(jobs_to_retry)

    def start_build_for_jobs(self, jobs_to_build):
        """Start build process for specific jobs."""
        # Load settings
        import json
        settings_path = Path.home() / ".meta_injector_settings.json"
        if not settings_path.exists():
            error_msg = "설정 파일을 찾을 수 없습니다" if tr.current_language == "ko" else "Settings file not found"
            show_message(self, "warning", tr.get("error"), error_msg)
            return

        with open(settings_path, 'r') as f:
            settings = json.load(f)

        common_key = settings.get('common_key', '')
        if not common_key:
            error_msg = "Common Key가 설정되지 않았습니다" if tr.current_language == "ko" else "Common Key not set"
            show_message(self, "warning", tr.get("error"), error_msg)
            return

        # Get title keys
        title_keys = {}
        if settings.get('rhythm_heaven_key'):
            title_keys['Rhythm Heaven Fever (USA)'] = settings['rhythm_heaven_key']
        if settings.get('xenoblade_key'):
            title_keys['Xenoblade Chronicles (USA)'] = settings['xenoblade_key']
        if settings.get('galaxy2_key'):
            title_keys['Super Mario Galaxy 2 (EUR)'] = settings['galaxy2_key']

        if not title_keys:
            error_msg = "Title Key가 설정되지 않았습니다" if tr.current_language == "ko" else "No Title Key set"
            show_message(self, "warning", tr.get("error"), error_msg)
            return

        # Get output directory
        output_dir = settings.get('output_dir', '')
        if output_dir:
            output_path = Path(output_dir)
        else:
            # Use first game's directory as output
            output_path = jobs_to_build[0].game_path.parent

        self.current_output_dir = output_path

        # Create batch builder for retry jobs
        from .batch_builder import BatchBuilder
        self.batch_builder = BatchBuilder(
            jobs=jobs_to_build,
            common_key=common_key,
            title_keys=title_keys,
            output_dir=output_path,
            auto_icons=self.auto_icons_check.isChecked()
        )

        self.batch_builder.progress_updated.connect(self.on_progress)
        self.batch_builder.job_started.connect(self.on_job_started_by_job)
        self.batch_builder.job_finished.connect(self.on_job_finished_by_job)
        self.batch_builder.all_finished.connect(self.on_all_finished)

        # Disable UI during build
        self.set_ui_enabled(False)
        self.build_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.batch_builder.start()

    def on_job_started_by_job(self, job_index, game_name):
        """Handle job started signal for retry (uses job object index)."""
        # Find the actual row in the table for this job
        if job_index < len(self.batch_builder.jobs):
            job = self.batch_builder.jobs[job_index]
            for row, table_job in enumerate(self.jobs):
                if table_job is job:
                    self.on_job_started(row, game_name)
                    break

    def on_job_finished_by_job(self, job_index, success, message):
        """Handle job finished signal for retry (uses job object index)."""
        # Find the actual row in the table for this job
        if job_index < len(self.batch_builder.jobs):
            job = self.batch_builder.jobs[job_index]
            for row, table_job in enumerate(self.jobs):
                if table_job is job:
                    self.on_job_finished(row, success, message)
                    break

    def set_ui_enabled(self, enabled: bool):
        """Enable or disable UI elements during build."""
        # Disable/enable top buttons
        self.add_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
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

        settings_file = Path.home() / ".meta_injector_settings.json"
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
            # Base controller options (index 0-5)
            base_options = {
                0: "no_gamepad",     # 미적용 (Wiimote만)
                1: "none",           # 게임패드 (자연 CC 지원)
                2: "force_cc",       # 게임패드 (강제)
                3: "gamepad_lr",     # 게임패드 + LR (강제)
                4: "wiimote",        # 게임패드 Wiimote (세로)
                5: "horizontal_wiimote"  # 게임패드 Wiimote (가로)
            }
            
            if index in base_options:
                job.pad_option = base_options[index]
            elif index == 6:
                # Separator selected (shouldn't happen, but ignore)
                return
            else:
                # Dynamic GCT patch options (index 7+ after separator)
                gct_index = index - 7  # Account for separator at index 6
                if hasattr(job, 'available_gct_patches') and 0 <= gct_index < len(job.available_gct_patches):
                    _, patch_type = job.available_gct_patches[gct_index]
                    job.pad_option = patch_type
                else:
                    # No valid GCT patch found, keep current option
                    print(f"[WARN] Invalid GCT patch index {gct_index} for {job.title_name}")
                    return
            
            print(f"[INFO] Pad option for {job.title_name}: {job.pad_option}")

            # Update compatibility label/button for Galaxy patches
            self.update_compat_widget_for_galaxy(row, index)

            # Re-check for output path conflicts whenever pad option changes
            # Clear all existing conflict flags first
            for j in self.jobs:
                j.has_output_conflict = False

            # Detect conflicts again
            self.detect_output_conflicts()

            # Update table styling
            self.update_conflict_styling()

            # Update icon preview to reflect new badge (Galaxy/Gamepad)
            self.update_icon_preview(row, job)

    def update_compat_widget_for_galaxy(self, row, pad_index):
        """Update compatibility widget to show mapping button for Galaxy patches or label for CC patches."""
        if row >= len(self.jobs):
            return

        job = self.jobs[row]
        compat_widget = self.table.cellWidget(row, 4)
        if not compat_widget:
            return

        layout = compat_widget.layout()
        if not layout or layout.count() < 2:
            return

        # Get the first widget (compatibility label/button)
        old_widget = layout.itemAt(0).widget()
        if not old_widget:
            return

        # Check patch type based on job.pad_option (more reliable than pad_index)
        pad_option = job.pad_option or ""
        is_galaxy_allstars = "allstars" in pad_option
        is_galaxy_nvidia = "nvidia" in pad_option
        is_galaxy_patch = is_galaxy_allstars or is_galaxy_nvidia
        is_cc_patch = job.pad_option == "cc_patch" or (job.pad_option and job.pad_option.startswith("gct_"))

        if is_galaxy_patch:
            # Replace label/button with updated mapping button for Galaxy patches
            # Always update to ensure correct colors and images for AllStars/Nvidia
            # Remove old widget (could be label or button from previous selection)
            layout.removeWidget(old_widget)
            old_widget.deleteLater()

            # Create mapping button
            mapping_btn = QPushButton()
            mapping_btn.setFixedHeight(22)
            if tr.current_language == "ko":
                mapping_btn.setText("🎮 매핑 확인")
            else:
                mapping_btn.setText("🎮 View Mapping")

            # Different colors for AllStars (blue) and Nvidia (green)
            if is_galaxy_allstars:  # AllStars - Blue
                button_style = """
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5b9bd5, stop:1 #4a8bc2);
                        color: white;
                        font-size: 11px;
                        font-weight: 600;
                        padding: 4px 8px;
                        border: 1px solid #3d7ba8;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6babe5, stop:1 #5b9bd5);
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a8bc2, stop:1 #3d7ba8);
                    }
                """
            else:  # Nvidia - Green
                button_style = """
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5cb85c, stop:1 #4cae4c);
                        color: white;
                        font-size: 11px;
                        font-weight: 600;
                        padding: 4px 8px;
                        border: 1px solid #3d8b3d;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6cc76c, stop:1 #5cb85c);
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a9d4a, stop:1 #3d8b3d);
                    }
                """

            mapping_btn.setStyleSheet(button_style)
            mapping_btn.setCursor(Qt.PointingHandCursor)

            # Determine which image to show (0=AllStars, 1=Nvidia)
            image_index = 0 if is_galaxy_allstars else 1
            mapping_btn.clicked.connect(lambda checked, idx=image_index: self.show_galaxy_mapping(idx))

            layout.insertWidget(0, mapping_btn)
        elif is_cc_patch:
            # Show "GCT Patch Exists" label for CC patches (no mapping needed)
            layout.removeWidget(old_widget)
            old_widget.deleteLater()

            # Create CC patch label - no mapping button, just indicate patch exists
            if tr.current_language == "ko":
                cc_label_text = "🎮 GCT 패치 사용"
            else:
                cc_label_text = "🎮 GCT Patch Active"

            cc_label = QLabel(cc_label_text)
            cc_label.setAlignment(Qt.AlignCenter)
            cc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            cc_label.setFixedHeight(22)
            # Orange style for CC patches - stands out
            cc_label.setStyleSheet("background-color: #fff0c8; font-size: 11px; font-weight: 600; padding: 1px 4px; border-radius: 3px; border: 1px solid #e0a020;")

            layout.insertWidget(0, cc_label)
        else:
            # Restore compatibility label for non-patch options
            if isinstance(old_widget, QPushButton) or (isinstance(old_widget, QLabel) and
                ("GCT" in old_widget.text() or "매핑" in old_widget.text() or "Mapping" in old_widget.text())):
                # Remove button or CC label
                layout.removeWidget(old_widget)
                old_widget.deleteLater()

                # Restore compatibility label
                compat_label = QLabel(job.gamepad_compatibility)
                compat_label.setAlignment(Qt.AlignCenter)
                compat_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                compat_label.setFixedHeight(22)

                # Apply styling based on compatibility
                if 'works' in job.gamepad_compatibility.lower() and 'doesn\'t' not in job.gamepad_compatibility.lower():
                    compat_label.setStyleSheet("background-color: #c8ffc8; font-size: 11px; padding: 1px 4px; border-radius: 3px; border: 1px solid #80c080;")
                elif 'classic' in job.gamepad_compatibility.lower() or 'lr' in job.gamepad_compatibility.lower():
                    compat_label.setStyleSheet("background-color: #ffffc8; font-size: 11px; padding: 1px 4px; border-radius: 3px; border: 1px solid #c0c080;")
                elif 'unknown' in job.gamepad_compatibility.lower():
                    compat_label.setStyleSheet("background-color: #dcdcdc; font-size: 11px; padding: 1px 4px; border-radius: 3px; border: 1px solid #a0a0a0;")
                else:
                    compat_label.setStyleSheet("background-color: #ffc8c8; font-size: 11px; padding: 1px 4px; border-radius: 3px; border: 1px solid #c08080;")

                layout.insertWidget(0, compat_label)

    def show_galaxy_mapping(self, image_index):
        """Show Galaxy mapping dialog with only the specified image."""
        dialog = GamepadHelpDialog(self, initial_index=image_index, single_image_mode=True)
        dialog.exec_()

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
                job.icon_edited = True  # Force reprocessing - user explicitly changed the image
                self.update_icon_preview(row, job)
                print(f"[USER EDIT] Icon updated for {job.game_path.name}: {icon_path}")

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
                job.banner_edited = True  # Force reprocessing - user explicitly changed the image
                self.update_icon_preview(row, job)
                print(f"[USER EDIT] Banner updated for {job.game_path.name}: {banner_path}")