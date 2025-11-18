"""Batch build window - Simplified UI for mass injection."""
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QLabel, QCheckBox, QFileDialog, QMessageBox, QLineEdit, QDialog,
    QFormLayout, QStyle, QProgressDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap, QIcon, QFont
from .batch_builder import BatchBuilder, BatchBuildJob
from .game_info import game_info_extractor
from .compatibility_db import compatibility_db
from .paths import paths
from .translations import tr


class GameLoaderThread(QThread):
    """Background thread for loading game files one by one."""

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
        """Load games in background."""
        loaded_count = 0
        total = len(self.file_paths)

        for idx, file_path in enumerate(self.file_paths):
            # Check if stop requested
            if self.should_stop:
                print(f"[INFO] Loading stopped by user at {idx+1}/{total}")
                break

            self.progress_updated.emit(idx + 1, total)

            try:
                game_path = Path(file_path)

                # Extract game info
                game_info = game_info_extractor.extract_game_info(game_path)

                if not game_info:
                    print(f"[WARN] Failed to extract info from {game_path.name}")
                    continue

                # Create job
                job = BatchBuildJob(game_path, game_info)

                # Prepare metadata (quick operation)
                self.prepare_job_metadata(job)

                # Download icon if enabled
                if self.auto_download_icons:
                    self.download_icon_for_job(job)

                # Emit signal with completed job
                self.game_loaded.emit(job)
                loaded_count += 1

            except Exception as e:
                print(f"[ERROR] Failed to load {file_path}: {e}")
                import traceback
                traceback.print_exc()

        self.loading_finished.emit(loaded_count)

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

        # Set title name (Korean from DB if available)
        if found_game and found_game['title']:
            korean_title = found_game['title'].split('(')[0].strip()
            job.title_name = korean_title
        else:
            job.title_name = game_title

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
            return False

        repo_id = game_id[:4]
        system_type = job.game_info.get('system', 'wii')

        # First check local resources/wii/ directory
        local_wii_dir = resources.resources_dir / "wii"
        if local_wii_dir.exists():
            local_icon = local_wii_dir / "banner" / f"{repo_id}.png"
            local_banner = local_wii_dir / "banner" / f"{repo_id}.png"

            if local_icon.exists() and local_banner.exists():
                print(f"  [LOCAL] Found local images for {repo_id}")
                paths.temp_source.mkdir(parents=True, exist_ok=True)

                # Copy icon
                icon_path = paths.temp_source / f"icon_{game_id}.png"
                shutil.copy(local_icon, icon_path)
                job.icon_path = icon_path

                # Copy banner
                banner_path = paths.temp_source / f"banner_{game_id}.png"
                shutil.copy(local_banner, banner_path)
                job.banner_path = banner_path

                return True

        # If not found locally, try remote download
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        alternative_ids = list(GameTdb.get_alternative_ids(repo_id))

        for try_id in alternative_ids:
            icon_url = f"https://raw.githubusercontent.com/UWUVCI-PRIME/UWUVCI-IMAGES/master/{system_type}/{try_id}/iconTex.png"
            banner_url = f"https://raw.githubusercontent.com/UWUVCI-PRIME/UWUVCI-IMAGES/master/{system_type}/{try_id}/bootTvTex.png"

            try:
                paths.temp_source.mkdir(parents=True, exist_ok=True)

                # Download icon
                req = urllib.request.Request(
                    icon_url,
                    headers={'User-Agent': 'WiiVC-Injector/1.0'}
                )
                with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                    icon_data = response.read()
                    icon_path = paths.temp_source / f"icon_{game_id}.png"
                    icon_path.write_bytes(icon_data)
                    job.icon_path = icon_path

                # Download banner
                req = urllib.request.Request(
                    banner_url,
                    headers={'User-Agent': 'WiiVC-Injector/1.0'}
                )
                with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                    banner_data = response.read()
                    banner_path = paths.temp_source / f"banner_{game_id}.png"
                    banner_path.write_bytes(banner_data)
                    job.banner_path = banner_path

                print(f"  [OK] Downloaded icon+banner for {try_id}")
                return True

            except:
                continue

        # If download failed, use default images
        print(f"  [DEFAULT] Using default images for {game_id}")
        default_icon = resources.resources_dir / "images" / "logo.png"
        default_banner = resources.resources_dir / "images" / "logo.png"

        if default_icon.exists():
            icon_path = paths.temp_source / f"icon_{game_id}.png"
            shutil.copy(default_icon, icon_path)
            job.icon_path = icon_path

        if default_banner.exists():
            banner_path = paths.temp_source / f"banner_{game_id}.png"
            shutil.copy(default_banner, banner_path)
            job.banner_path = banner_path

        return True


class SimpleKeysDialog(QDialog):
    """Simple dialog for entering encryption keys."""

    def __init__(self, parent=None):
        super().__init__(parent)
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

    def save(self):
        """Save keys and close."""
        import json

        common_key = self.common_key_input.text().strip()
        if not common_key:
            error_msg = "Wii U Common Key가 필요합니다!" if tr.current_language == "ko" else "Wii U Common Key is required!"
            QMessageBox.warning(self, tr.get("error"), error_msg)
            return

        # Check if at least Rhythm Heaven key is provided (required)
        rhythm_key = self.rhythm_key_input.text().strip()
        xenoblade_key = self.xenoblade_key_input.text().strip()
        galaxy_key = self.galaxy_key_input.text().strip()

        if not rhythm_key:
            error_msg = "Rhythm Heaven Fever 타이틀 키는 필수입니다!" if tr.current_language == "ko" else "Rhythm Heaven Fever title key is required!"
            QMessageBox.warning(self, tr.get("error"), error_msg)
            return

        # Save to settings file
        settings = {
            'wii_u_common_key': common_key,
            'title_key_rhythm_heaven': rhythm_key,
            'title_key_xenoblade': xenoblade_key,
            'title_key_galaxy2': galaxy_key
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
            QMessageBox.warning(self, tr.get("error"), error_msg)
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

                print("[DEBUG] Loaded existing settings into dialog")
        except Exception as e:
            print(f"[WARN] Failed to load existing settings: {e}")


class EditGameDialog(QDialog):
    """Dialog to edit individual game metadata."""

    def __init__(self, job: BatchBuildJob, parent=None):
        super().__init__(parent)
        self.job = job
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        title_text = "게임 메타데이터 편집" if tr.current_language == "ko" else "Edit Game Metadata"
        self.setWindowTitle(title_text)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Title
        title_layout = QHBoxLayout()
        game_title_text = "게임 제목:" if tr.current_language == "ko" else "Game Title:"
        title_layout.addWidget(QLabel(game_title_text))
        self.title_input = QLineEdit(self.job.title_name)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        # Title ID
        id_layout = QHBoxLayout()
        title_id_text = "타이틀 ID:" if tr.current_language == "ko" else "Title ID:"
        id_layout.addWidget(QLabel(title_id_text))
        self.id_input = QLineEdit(self.job.title_id)
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(tr.get("save"))
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton(tr.get("cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save(self):
        """Save changes."""
        self.job.title_name = self.title_input.text()
        self.job.title_id = self.id_input.text()
        self.accept()


class BatchWindow(QMainWindow):
    """Simplified batch build window."""

    def __init__(self):
        super().__init__()
        self.jobs = []
        self.batch_builder = None
        self.loader_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle(tr.get("app_title") + " - " + (tr.get("batch_converter_title") if tr.current_language == "ko" else "Batch Mode"))
        self.setGeometry(100, 100, 900, 600)

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

        add_btn = QPushButton(tr.get("add_files"))
        add_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_btn.setStyleSheet(btn_style)
        add_btn.clicked.connect(self.add_games)
        top_layout.addWidget(add_btn)

        remove_btn = QPushButton(tr.get("remove_selected"))
        remove_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        remove_btn.setStyleSheet(btn_style)
        remove_btn.clicked.connect(self.remove_selected)
        top_layout.addWidget(remove_btn)

        clear_btn = QPushButton(tr.get("clear_all"))
        clear_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        clear_btn.setStyleSheet(btn_style)
        clear_btn.clicked.connect(self.clear_all)
        top_layout.addWidget(clear_btn)

        top_layout.addStretch()

        # Settings button
        settings_text = "⚙ " + ("설정" if tr.current_language == "ko" else "Settings")
        settings_btn = QPushButton(settings_text)
        settings_btn.setStyleSheet(btn_style)
        settings_btn.clicked.connect(self.show_settings)
        top_layout.addWidget(settings_btn)

        auto_download_text = "아이콘 자동 다운로드" if tr.current_language == "ko" else "Auto Download Icons"
        self.auto_icons_check = QCheckBox(auto_download_text)
        self.auto_icons_check.setChecked(True)
        top_layout.addWidget(self.auto_icons_check)

        layout.addLayout(top_layout)

        # Game list table
        self.table = QTableWidget()
        self.table.setColumnCount(8)

        if tr.current_language == "ko":
            headers = ["파일 이름", "아이콘", "배너", "게임 제목", "타이틀 ID", "게임패드", "상태", "작업"]
        else:
            headers = ["File Name", "Icon", "Banner", "Game Title", "Title ID", "Gamepad", "Status", "Actions"]

        self.table.setHorizontalHeaderLabels(headers)
        # Set column widths
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # File Name
        self.table.setColumnWidth(1, 80)  # Icon preview
        self.table.setColumnWidth(2, 120)  # Banner preview (16:9 ratio)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Game Title
        self.table.setColumnWidth(4, 140)  # Title ID
        self.table.setColumnWidth(5, 100)  # Gamepad
        self.table.setColumnWidth(6, 100)  # Status
        self.table.setColumnWidth(7, 80)  # Actions
        self.table.setRowHeight(0, 70)  # Taller rows for preview
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self.edit_game)
        self.table.cellClicked.connect(self.on_cell_clicked)
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

        build_text = "빌드 시작" if tr.current_language == "ko" else "Start Batch Build"
        self.build_btn = QPushButton(build_text)
        self.build_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
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

        stop_text = "중지" if tr.current_language == "ko" else "Stop"
        self.stop_btn = QPushButton(stop_text)
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
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
            QMessageBox.information(self, title, msg)

        if not new_file_paths:
            return

        # Show loading status
        if tr.current_language == "ko":
            self.status_label.setText(f"{len(new_file_paths)}개 게임 로딩 중...")
        else:
            self.status_label.setText(f"Loading {len(new_file_paths)} games...")

        # Create progress dialog
        if tr.current_language == "ko":
            progress_label = "게임 추가 중..."
            cancel_label = "취소"
        else:
            progress_label = "Adding games..."
            cancel_label = "Cancel"

        self.loading_progress = QProgressDialog(
            progress_label,
            cancel_label,
            0,
            len(new_file_paths),
            self
        )
        self.loading_progress.setWindowModality(Qt.WindowModal)
        self.loading_progress.setMinimumDuration(500)  # Show after 500ms
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
        if hasattr(self, 'loading_progress'):
            self.loading_progress.setValue(current)
            if tr.current_language == "ko":
                self.loading_progress.setLabelText(f"게임 추가 중... ({current}/{total})")
            else:
                self.loading_progress.setLabelText(f"Adding games... ({current}/{total})")

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
        # Update icon (Column 1)
        if job.icon_path and job.icon_path.exists():
            pixmap = QPixmap(str(job.icon_path))
            scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_item = QTableWidgetItem()
            icon_item.setData(Qt.DecorationRole, scaled_pixmap)
            icon_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, icon_item)
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
            self.table.setItem(row, 1, icon_item)

        # Update banner (Column 2)
        if job.banner_path and job.banner_path.exists():
            pixmap = QPixmap(str(job.banner_path))
            scaled_pixmap = pixmap.scaled(120, 67, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            banner_item = QTableWidgetItem()
            banner_item.setData(Qt.DecorationRole, scaled_pixmap)
            banner_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, banner_item)
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
            self.table.setItem(row, 2, banner_item)

    def add_job_to_table(self, job: BatchBuildJob):
        """Add job to table and return row index."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 70)  # Taller rows for icon preview

        # Column 0: File name
        self.table.setItem(row, 0, QTableWidgetItem(job.game_path.name))

        # Column 1: Icon preview
        icon_item = QTableWidgetItem("Loading...")
        icon_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, icon_item)

        # Column 2: Banner preview
        banner_item = QTableWidgetItem("Loading...")
        banner_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, banner_item)

        # Column 3: Game title
        self.table.setItem(row, 3, QTableWidgetItem(job.title_name))

        # Column 4: Title ID (with Game ID)
        game_id = job.game_info.get('game_id', '') if job.game_info else ''
        title_id_text = f"{job.title_id}\n({game_id})" if game_id else job.title_id
        self.table.setItem(row, 4, QTableWidgetItem(title_id_text))

        # Column 5: Gamepad compatibility
        gamepad_item = QTableWidgetItem(job.gamepad_compatibility)
        # Color code based on compatibility
        if 'works' in job.gamepad_compatibility.lower():
            gamepad_item.setBackground(QColor(200, 255, 200))  # Light green
        elif 'classic' in job.gamepad_compatibility.lower() or 'lr' in job.gamepad_compatibility.lower():
            gamepad_item.setBackground(QColor(255, 255, 200))  # Light yellow
        elif 'unknown' in job.gamepad_compatibility.lower():
            gamepad_item.setBackground(QColor(220, 220, 220))  # Light gray
        else:
            gamepad_item.setBackground(QColor(255, 200, 200))  # Light red
        self.table.setItem(row, 5, gamepad_item)

        # Column 6: Status
        status_text = "대기 중" if tr.current_language == "ko" else "Pending"
        status_item = QTableWidgetItem(status_text)
        status_item.setBackground(QColor(255, 249, 196))  # Yellow
        self.table.setItem(row, 6, status_item)

        # Column 7: Edit button
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
        edit_btn.clicked.connect(lambda r=row: self.edit_game_by_row(r))
        self.table.setCellWidget(row, 7, edit_btn)

        return row

    def edit_game(self, row, column):
        """Edit game metadata."""
        if row < len(self.jobs):
            dialog = EditGameDialog(self.jobs[row], self)
            if dialog.exec_():
                # Update table
                self.table.item(row, 1).setText(self.jobs[row].title_name)
                self.table.item(row, 2).setText(self.jobs[row].title_id)

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

        reply = QMessageBox.question(
            self,
            title,
            msg,
            QMessageBox.Yes | QMessageBox.No
        )

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
                    QMessageBox.warning(self, tr.get("error"), msg)
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
            QMessageBox.warning(self, tr.get("error"), msg)
            return

        # Get output directory
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

        self.batch_builder = BatchBuilder(
            self.jobs,
            common_key,
            title_keys,
            Path(output_dir),
            self.auto_icons_check.isChecked()
        )

        self.batch_builder.progress_updated.connect(self.on_progress)
        self.batch_builder.job_started.connect(self.on_job_started)
        self.batch_builder.job_finished.connect(self.on_job_finished)
        self.batch_builder.all_finished.connect(self.on_all_finished)

        self.batch_builder.start()

    def stop_build(self):
        """Stop batch build."""
        if self.batch_builder:
            self.batch_builder.stop()

    def on_progress(self, current, total, message):
        """Handle progress update."""
        progress = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)

    def on_job_started(self, idx, game_name):
        """Handle job started."""
        if idx < self.table.rowCount():
            status_item = self.table.item(idx, 6)
            status_text = "빌드 중..." if tr.current_language == "ko" else "Building..."
            status_item.setText(status_text)
            status_item.setBackground(QColor(173, 216, 230))  # Light blue

    def on_job_finished(self, idx, success, message):
        """Handle job finished."""
        if idx < self.table.rowCount():
            status_item = self.table.item(idx, 6)
            if success:
                status_text = "완료" if tr.current_language == "ko" else "Completed"
                status_item.setText(status_text)
                status_item.setBackground(QColor(200, 230, 201))  # Green
            else:
                failed_text = "실패" if tr.current_language == "ko" else "Failed"
                status_item.setText(f"{failed_text}: {message}")
                status_item.setBackground(QColor(255, 205, 210))  # Red

    def on_all_finished(self, success_count, total_count):
        """Handle all jobs finished."""
        self.build_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)

        if tr.current_language == "ko":
            self.status_label.setText(f"완료: {success_count}/{total_count} 성공")
            title = "일괄 빌드 완료"
            msg = f"빌드 완료!\n\n성공: {success_count}\n실패: {total_count - success_count}\n전체: {total_count}"
        else:
            self.status_label.setText(f"Completed: {success_count}/{total_count} succeeded")
            title = "Batch Build Complete"
            msg = f"Build finished!\n\nSuccess: {success_count}\nFailed: {total_count - success_count}\nTotal: {total_count}"

        QMessageBox.information(self, title, msg)

    def show_settings(self):
        """Show settings dialog for encryption keys."""
        dialog = SimpleKeysDialog(self)
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

