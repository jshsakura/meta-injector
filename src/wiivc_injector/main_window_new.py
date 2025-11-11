"""Redesigned modern main window for WiiVC Injector."""
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QRadioButton,
    QLineEdit, QCheckBox, QFileDialog, QProgressBar,
    QGroupBox, QMessageBox, QApplication, QScrollArea,
    QButtonGroup, QFrame, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from .settings_dialog import SettingsDialog
from .sdcard_dialog_new import ModernSDCardDialog
from .compatibility_dialog import CompatibilityDialog
from .compatibility_db import compatibility_db
from .paths import paths
from .resources import resources
from .image_utils import image_processor
from .game_info import game_info_extractor
from .build_engine import BuildEngine
from .batch_builder import BatchBuilder, BatchBuildJob
from .translations import tr


class BuildThread(QThread):
    """Background thread for building WiiVC inject."""

    # Signals
    progress_updated = pyqtSignal(int, str)  # percent, message
    build_finished = pyqtSignal(bool, str)  # success, output_dir

    def __init__(self, game_path, system_type, output_dir, common_key, title_key,
                 title_name, title_id, options):
        super().__init__()
        self.game_path = game_path
        self.system_type = system_type
        self.output_dir = output_dir
        self.common_key = common_key
        self.title_key = title_key
        self.title_name = title_name
        self.title_id = title_id
        self.options = options

    def run(self):
        """Run build in background thread."""
        def progress_callback(percent, message):
            self.progress_updated.emit(percent, message)

        engine = BuildEngine(paths, progress_callback)

        success = engine.build(
            game_path=self.game_path,
            system_type=self.system_type,
            output_dir=self.output_dir,
            common_key=self.common_key,
            title_key=self.title_key,
            title_name=self.title_name,
            title_id=self.title_id,
            options=self.options
        )

        self.build_finished.emit(success, str(self.output_dir))


class ModernWiiVCInjector(QMainWindow):
    """Modern redesigned WiiVC Injector window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr.get("app_title"))
        self.setGeometry(100, 100, 1000, 650)
        self.setMaximumWidth(1150)

        # Set modern color scheme
        self.setup_style()

        # Initialize state
        self.init_state()

        # Build UI
        self.init_ui()

        # Initialize directories
        self.init_temp_directories()

        # Load saved keys
        self.load_saved_keys()

    def setup_style(self):
        """Setup modern styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px 24px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 140px;
                font-size: 10pt;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLineEdit, QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 10pt;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #2196F3;
            }
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: 10pt;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QLabel {
                color: #333333;
                font-size: 10pt;
            }
            QRadioButton {
                spacing: 8px;
                padding: 5px;
                font-size: 10pt;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox {
                spacing: 8px;
                padding: 5px;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)

    def init_state(self):
        """Initialize application state."""
        self.system_type = "wii"
        self.title_id_hex = ""
        self.title_id_text = ""
        self.internal_game_name = ""
        self.cucholix_repo_id = ""
        self.flag_game_specified = False
        self.flag_icon_specified = False
        self.flag_banner_specified = False
        self.flag_drc_specified = False
        self.flag_logo_specified = False
        self.flag_boot_sound_specified = False
        self.flag_gc2_specified = False

        # Paths
        self.game_source_path = ""
        self.icon_source_path = ""
        self.banner_source_path = ""
        self.drc_source_path = ""
        self.logo_source_path = ""
        self.boot_sound_path = ""
        self.gc2_source_path = ""
        self.main_dol_path = ""

        # Repository URL
        self.repo_url = "https://raw.githubusercontent.com/UWUVCI-PRIME/UWUVCI-IMAGES/master/"

    def init_ui(self):
        """Build the UI."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header with system type selection
        header = self.create_header()
        layout.addWidget(header)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_source_tab()
        self.create_images_tab()
        self.create_meta_tab()
        self.create_advanced_tab()
        self.create_build_tab()

        # Bottom buttons
        bottom = self.create_bottom_buttons()
        layout.addWidget(bottom)

        # Connect signals
        self.connect_signals()

    def create_header(self):
        """Create header with system type selection."""
        header = QGroupBox(tr.get("system_type"))
        layout = QHBoxLayout()

        self.system_group = QButtonGroup()

        self.wii_retail_radio = QRadioButton(tr.get("wii_retail"))
        self.wii_retail_radio.setChecked(True)
        self.gc_retail_radio = QRadioButton(tr.get("gc_retail"))

        self.system_group.addButton(self.wii_retail_radio)
        self.system_group.addButton(self.gc_retail_radio)

        layout.addWidget(self.wii_retail_radio)
        layout.addWidget(self.gc_retail_radio)
        layout.addStretch()

        header.setLayout(layout)
        return header

    def create_source_tab(self):
        """Create source files tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Game file
        game_group = self.create_file_selector(
            tr.get("game_iso_wbfs"),
            tr.get("no_game_file_selected"),
            self.select_game_file,
            show_preview=False
        )
        self.game_label = game_group.findChild(QLabel, "file_label")
        layout.addWidget(game_group)

        # Game info display
        info_group = QGroupBox(tr.get("game_information"))
        info_layout = QVBoxLayout()
        self.game_name_display = QLabel(tr.get("internal_name_na"))
        self.game_id_display = QLabel(tr.get("title_id_na"))
        info_layout.addWidget(self.game_name_display)
        info_layout.addWidget(self.game_id_display)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Icon and Banner in one row
        images_group = QGroupBox(tr.get("icon_banner_images"))
        images_main_layout = QVBoxLayout()
        images_main_layout.setSpacing(6)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        icon_btn = QPushButton(f"📷 {tr.get('manual_icon')}")
        icon_btn.clicked.connect(self.select_icon_file)
        icon_btn.setMinimumWidth(140)
        btn_row.addWidget(icon_btn)

        banner_btn = QPushButton(f"🖼 {tr.get('manual_banner')}")
        banner_btn.clicked.connect(self.select_banner_file)
        banner_btn.setMinimumWidth(150)
        btn_row.addWidget(banner_btn)

        # Repository download button
        repo_btn = QPushButton(f"📥 {tr.get('auto_download')}")
        repo_btn.setStyleSheet("QPushButton { background-color: #FF9800; }")
        repo_btn.setMinimumWidth(150)
        repo_btn.clicked.connect(self.download_from_repo)
        btn_row.addWidget(repo_btn)

        btn_row.addStretch()
        images_main_layout.addLayout(btn_row)

        # Preview row
        preview_row = QHBoxLayout()
        preview_row.setSpacing(12)

        # Icon preview
        icon_container = QWidget()
        icon_vlayout = QVBoxLayout(icon_container)
        icon_vlayout.setContentsMargins(0, 0, 0, 0)
        icon_vlayout.setSpacing(4)
        self.icon_label = QLabel(tr.get("no_icon"))
        self.icon_label.setObjectName("file_label")
        self.icon_label.setStyleSheet("color: #888; font-size: 8pt;")
        self.icon_label.setWordWrap(True)
        icon_vlayout.addWidget(self.icon_label)
        self.icon_preview = QLabel()
        self.icon_preview.setObjectName("preview_label")
        self.icon_preview.setFixedSize(100, 100)
        self.icon_preview.setStyleSheet("background-color: #333; border: 1px solid #ccc; border-radius: 2px;")
        self.icon_preview.setAlignment(Qt.AlignCenter)
        self.icon_preview.setScaledContents(True)
        icon_vlayout.addWidget(self.icon_preview)
        preview_row.addWidget(icon_container, 2)

        # Banner preview
        banner_container = QWidget()
        banner_vlayout = QVBoxLayout(banner_container)
        banner_vlayout.setContentsMargins(0, 0, 0, 0)
        banner_vlayout.setSpacing(4)
        self.banner_label = QLabel(tr.get("no_banner"))
        self.banner_label.setObjectName("file_label")
        self.banner_label.setStyleSheet("color: #888; font-size: 8pt;")
        self.banner_label.setWordWrap(True)
        banner_vlayout.addWidget(self.banner_label)
        self.banner_preview = QLabel()
        self.banner_preview.setObjectName("preview_label")
        self.banner_preview.setFixedSize(356, 100)
        self.banner_preview.setStyleSheet("background-color: #333; border: 1px solid #ccc; border-radius: 2px;")
        self.banner_preview.setAlignment(Qt.AlignCenter)
        self.banner_preview.setScaledContents(True)
        banner_vlayout.addWidget(self.banner_preview)
        preview_row.addWidget(banner_container, 8)

        images_main_layout.addLayout(preview_row)
        images_group.setLayout(images_main_layout)
        layout.addWidget(images_group)

        layout.addStretch()
        self.tabs.addTab(scroll, tr.get("tab_source_files"))

    def create_images_tab(self):
        """Create additional images tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # DRC Image
        drc_group = self.create_file_selector(
            tr.get("drc_image"),
            tr.get("no_drc_image"),
            self.select_drc_file,
            preview_size=(256, 144)
        )
        self.drc_label = drc_group.findChild(QLabel, "file_label")
        self.drc_preview = drc_group.findChild(QLabel, "preview_label")
        layout.addWidget(drc_group)

        # Logo
        logo_group = self.create_file_selector(
            tr.get("logo_image"),
            tr.get("no_logo"),
            self.select_logo_file,
            preview_size=(170, 42)
        )
        self.logo_label = logo_group.findChild(QLabel, "file_label")
        self.logo_preview = logo_group.findChild(QLabel, "preview_label")
        layout.addWidget(logo_group)

        # Boot Sound
        sound_group = QGroupBox(tr.get("boot_sound"))
        sound_layout = QVBoxLayout()
        sound_btn_layout = QHBoxLayout()
        self.boot_sound_btn = QPushButton(tr.get("select_wav_file"))
        self.boot_sound_btn.clicked.connect(self.select_boot_sound_file)
        self.boot_sound_preview_btn = QPushButton(f"▶ {tr.get('preview')}")
        self.boot_sound_preview_btn.setEnabled(False)
        sound_btn_layout.addWidget(self.boot_sound_btn)
        sound_btn_layout.addWidget(self.boot_sound_preview_btn)
        self.boot_sound_label = QLabel(tr.get("no_sound_file"))
        self.boot_sound_loop = QCheckBox(tr.get("loop_boot_sound"))
        sound_layout.addLayout(sound_btn_layout)
        sound_layout.addWidget(self.boot_sound_label)
        sound_layout.addWidget(self.boot_sound_loop)
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)

        # GC Second Disc
        gc2_group = self.create_file_selector(
            tr.get("second_disc_gc"),
            tr.get("no_second_disc"),
            self.select_gc2_file,
            show_preview=False
        )
        self.gc2_label = gc2_group.findChild(QLabel, "file_label")
        layout.addWidget(gc2_group)

        layout.addStretch()
        self.tabs.addTab(scroll, tr.get("tab_images_sound"))

    def create_meta_tab(self):
        """Create meta information tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Title
        title_group = QGroupBox(tr.get("game_title"))
        title_layout = QVBoxLayout()
        self.packed_title_line1 = QLineEdit()
        self.packed_title_line1.setPlaceholderText(tr.get("enter_game_title"))
        self.enable_packed_line2 = QCheckBox(tr.get("enable_second_line"))
        self.packed_title_line2 = QLineEdit()
        self.packed_title_line2.setPlaceholderText(tr.get("optional_second_line"))
        self.packed_title_line2.setEnabled(False)
        self.enable_packed_line2.toggled.connect(self.packed_title_line2.setEnabled)
        title_layout.addWidget(QLabel(tr.get("title_line_1")))
        title_layout.addWidget(self.packed_title_line1)
        title_layout.addWidget(self.enable_packed_line2)
        title_layout.addWidget(QLabel(tr.get("title_line_2")))
        title_layout.addWidget(self.packed_title_line2)
        title_group.setLayout(title_layout)
        layout.addWidget(title_group)

        # Title ID
        tid_group = QGroupBox(tr.get("title_id"))
        tid_layout = QVBoxLayout()
        self.packed_title_id_line = QLineEdit()
        self.packed_title_id_line.setPlaceholderText(tr.get("title_id_placeholder"))
        self.packed_title_id_line.setMaxLength(16)
        tid_layout.addWidget(self.packed_title_id_line)
        tid_group.setLayout(tid_layout)
        layout.addWidget(tid_group)

        # GamePad Emulation
        gamepad_group = QGroupBox(tr.get("gamepad_emulation_mode"))
        gamepad_layout = QVBoxLayout()

        self.gamepad_group = QButtonGroup()
        self.no_gamepad_emu = QRadioButton(tr.get("no_emulation"))
        self.cc_emu = QRadioButton(tr.get("cc_emulation"))
        self.force_cc = QRadioButton(tr.get("force_cc"))
        self.force_cc.setChecked(True)  # Default: Force Classic Controller
        self.force_no_cc = QRadioButton(tr.get("force_no_cc"))
        self.hor_wiimote = QRadioButton(tr.get("horizontal_wiimote"))
        self.ver_wiimote = QRadioButton(tr.get("vertical_wiimote"))

        for rb in [self.no_gamepad_emu, self.cc_emu, self.force_cc,
                   self.force_no_cc, self.hor_wiimote, self.ver_wiimote]:
            self.gamepad_group.addButton(rb)
            gamepad_layout.addWidget(rb)

        gamepad_group.setLayout(gamepad_layout)
        layout.addWidget(gamepad_group)

        # LR Patch
        self.lr_patch = QCheckBox(tr.get("enable_lr_patch"))
        layout.addWidget(self.lr_patch)

        layout.addStretch()
        self.tabs.addTab(scroll, tr.get("tab_meta_info"))

    def create_advanced_tab(self):
        """Create advanced options tab (simplified for Wii/GC retail)."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Simplified options for retail injection
        options_group = QGroupBox(tr.get("advanced_options"))
        options_layout = QVBoxLayout()

        # Essential options only
        self.c2w_patch_flag = QCheckBox(tr.get("enable_c2w_patcher"))
        self.custom_main_dol = QCheckBox(tr.get("use_custom_main_dol"))
        self.disable_trimming = QCheckBox(tr.get("disable_iso_trimming"))

        # Add helpful description labels
        desc_font = QFont()
        desc_font.setPointSize(9)

        c2w_desc = QLabel("  └ " + tr.get("c2w_description"))
        c2w_desc.setFont(desc_font)
        c2w_desc.setStyleSheet("color: #666; margin-left: 20px;")

        trimming_desc = QLabel("  └ " + tr.get("trimming_description"))
        trimming_desc.setFont(desc_font)
        trimming_desc.setStyleSheet("color: #666; margin-left: 20px;")

        options_layout.addWidget(self.c2w_patch_flag)
        options_layout.addWidget(c2w_desc)
        options_layout.addSpacing(8)
        options_layout.addWidget(self.disable_trimming)
        options_layout.addWidget(trimming_desc)
        options_layout.addSpacing(8)
        options_layout.addWidget(self.custom_main_dol)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Custom DOL selector
        dol_group = QGroupBox(tr.get("custom_main_dol_file"))
        dol_layout = QHBoxLayout()
        self.main_dol_btn = QPushButton(tr.get("select_dol_file"))
        self.main_dol_btn.setEnabled(False)
        self.main_dol_label = QLabel(tr.get("no_file_selected"))
        self.custom_main_dol.toggled.connect(self.main_dol_btn.setEnabled)
        self.main_dol_btn.clicked.connect(self.select_main_dol)
        dol_layout.addWidget(self.main_dol_btn)
        dol_layout.addWidget(self.main_dol_label, 1)
        dol_group.setLayout(dol_layout)
        layout.addWidget(dol_group)

        layout.addStretch()
        self.tabs.addTab(scroll, tr.get("tab_advanced"))

    def create_build_tab(self):
        """Create build tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Requirements check
        req_group = QGroupBox(tr.get("build_requirements"))
        req_layout = QVBoxLayout()
        self.source_check = QLabel(f"⚠ {tr.get('source_files_not_ready')}")
        self.meta_check = QLabel(f"⚠ {tr.get('meta_info_not_ready')}")
        self.keys_check = QLabel(f"⚠ {tr.get('encryption_keys_not_ready')}")
        self.advance_check = QLabel(f"✓ {tr.get('advanced_options_ok')}")

        for label in [self.source_check, self.meta_check, self.keys_check, self.advance_check]:
            font = QFont()
            font.setPointSize(10)
            label.setFont(font)
            req_layout.addWidget(label)

        req_group.setLayout(req_layout)
        layout.addWidget(req_group)

        # Encryption Keys
        keys_group = QGroupBox(tr.get("encryption_keys"))
        keys_layout = QVBoxLayout()

        # Common Key
        ck_layout = QHBoxLayout()
        ck_layout.addWidget(QLabel(tr.get("wii_u_common_key")))
        self.wii_u_common_key = QLineEdit()
        self.wii_u_common_key.setPlaceholderText(tr.get("common_key_placeholder"))
        self.wii_u_common_key.setMaxLength(32)
        self.save_common_key_btn = QPushButton(tr.get("verify_and_save"))
        self.save_common_key_btn.setMaximumWidth(120)
        self.save_common_key_btn.clicked.connect(self.save_common_key)
        ck_layout.addWidget(self.wii_u_common_key, 1)
        ck_layout.addWidget(self.save_common_key_btn)
        keys_layout.addLayout(ck_layout)

        # Title Key - 게임별 타이틀 키 (예: 리듬헤븐 피버)
        tk_layout = QHBoxLayout()
        tk_layout.addWidget(QLabel("Title Key:"))
        self.title_key_build = QLineEdit()
        self.title_key_build.setPlaceholderText("예: 리듬헤븐 피버 타이틀 키 (32자리 HEX)")
        self.title_key_build.setMaxLength(32)
        self.save_title_key_btn = QPushButton(tr.get("verify_and_save"))
        self.save_title_key_btn.setMaximumWidth(120)
        self.save_title_key_btn.clicked.connect(self.save_title_key_from_build_tab)
        tk_layout.addWidget(self.title_key_build, 1)
        tk_layout.addWidget(self.save_title_key_btn)
        keys_layout.addLayout(tk_layout)

        keys_group.setLayout(keys_layout)
        layout.addWidget(keys_group)

        # Progress
        progress_group = QGroupBox(tr.get("build_progress"))
        progress_layout = QVBoxLayout()
        self.build_progress = QProgressBar()
        self.build_progress.setMinimumHeight(30)
        self.build_status = QLabel(tr.get("ready_to_build"))
        self.build_status.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.build_progress)
        progress_layout.addWidget(self.build_status)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Build Button
        self.build_button = QPushButton(f"🚀 {tr.get('build_injection')}")
        self.build_button.setMinimumHeight(60)
        self.build_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                font-size: 16pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.build_button.clicked.connect(self.start_build)
        layout.addWidget(self.build_button)

        layout.addStretch()
        self.tabs.addTab(tab, tr.get("tab_build"))

        # Connect tab change event to update requirements
        self.tabs.currentChanged.connect(self.update_build_requirements)

    def create_bottom_buttons(self):
        """Create bottom button bar."""
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(frame)

        btn_layout = QHBoxLayout()

        # Language selector
        lang_label = QLabel(f"🌐 {tr.get('language')}:")
        btn_layout.addWidget(lang_label)

        self.language_combo = QComboBox()
        self.language_combo.setMinimumWidth(100)
        for lang_code, lang_name in tr.get_available_languages():
            self.language_combo.addItem(lang_name, lang_code)
        # Set current language
        current_index = 0 if tr.current_language == "en" else 1
        self.language_combo.setCurrentIndex(current_index)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        btn_layout.addWidget(self.language_combo)

        btn_layout.addSpacing(20)

        self.settings_btn = QPushButton(f"⚙ {tr.get('settings')}")
        self.settings_btn.setStyleSheet("QPushButton { background-color: #607D8B; }")
        self.sd_card_btn = QPushButton(f"💾 {tr.get('sd_card_utilities')}")
        self.sd_card_btn.setStyleSheet("QPushButton { background-color: #607D8B; }")
        self.compatibility_btn = QPushButton(f"📊 호환성 DB (Compatibility)")
        self.compatibility_btn.setStyleSheet("QPushButton { background-color: #4CAF50; }")

        btn_layout.addWidget(self.settings_btn)
        btn_layout.addWidget(self.sd_card_btn)
        btn_layout.addWidget(self.compatibility_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        return widget

    def create_file_selector(self, title, placeholder, callback,
                            preview_size=None, show_preview=True):
        """Create a file selector group with optional preview."""
        group = QGroupBox(title)
        layout = QVBoxLayout()

        # Button and label
        btn_layout = QHBoxLayout()
        btn = QPushButton(tr.get("browse"))
        btn.clicked.connect(callback)
        label = QLabel(placeholder)
        label.setObjectName("file_label")
        label.setStyleSheet("color: #757575; font-style: italic;")
        btn_layout.addWidget(btn)
        btn_layout.addWidget(label, 1)
        layout.addLayout(btn_layout)

        # Preview if requested
        if show_preview and preview_size:
            preview = QLabel()
            preview.setObjectName("preview_label")
            preview.setFixedSize(*preview_size)
            preview.setStyleSheet("background-color: #424242; border: 2px solid #e0e0e0;")
            preview.setAlignment(Qt.AlignCenter)
            preview.setScaledContents(True)
            layout.addWidget(preview)

        group.setLayout(layout)
        return group

    def connect_signals(self):
        """Connect all signals."""
        self.settings_btn.clicked.connect(self.show_settings)
        self.sd_card_btn.clicked.connect(self.show_sdcard_dialog)
        self.compatibility_btn.clicked.connect(self.show_compatibility_dialog)

        # System type changes
        self.wii_retail_radio.toggled.connect(self.on_system_type_changed)
        self.gc_retail_radio.toggled.connect(self.on_system_type_changed)

    def init_temp_directories(self):
        """Initialize temporary directories."""
        paths.create_temp_directories()

        # Verify tools exist
        if not (paths.temp_tools / "EXE").exists() or not (paths.temp_tools / "JAR").exists():
            print(f"WARNING: TOOLDIR not found at {paths.temp_tools}")
            print(f"Please ensure TOOLDIR folder exists in project root")
        else:
            print(f"✓ Tools ready at {paths.temp_tools}")

    # Event Handlers

    def on_system_type_changed(self):
        """Handle system type change."""
        if self.wii_retail_radio.isChecked():
            self.system_type = "wii"
        elif self.gc_retail_radio.isChecked():
            self.system_type = "gcn"

    def handle_nand_selection(self):
        """Handle NAND system type selection."""
        from PyQt5.QtWidgets import QInputDialog

        title_id, ok = QInputDialog.getText(
            self,
            tr.get("nand_title_id_title"),
            tr.get("nand_title_id_prompt"),
            text="XXXX"
        )

        if not ok or not title_id:
            # User cancelled, revert to Wii Retail
            self.wii_retail_radio.setChecked(True)
            self.system_type = "wii"
            return

        title_id = title_id.strip().upper()

        if len(title_id) != 4:
            QMessageBox.warning(
                self,
                tr.get("invalid_title_id"),
                tr.get("invalid_title_id_msg")
            )
            self.wii_retail_radio.setChecked(True)
            self.system_type = "wii"
            return

        # Set as game source
        self.game_label.setText(f"{tr.get('vwii_nand_title')} {title_id}")
        self.game_label.setStyleSheet("color: #2196F3; font-style: normal;")
        self.game_source_path = title_id
        self.flag_game_specified = True
        self.system_type = "wiiware"
        self.title_id_text = title_id
        # NAND uses the 4-letter title ID directly
        self.cucholix_repo_id = title_id

        # Convert to hex for packed title ID
        hex_id = ''.join(f'{ord(c):X}' for c in title_id)
        self.packed_title_id_line.setText(f"00050002{hex_id}")

        self.game_name_display.setText(tr.get("internal_name_nand"))
        self.game_id_display.setText(f"Title ID: {title_id}")

        print(f"NAND title selected: {title_id}")
        print(f"  - Repository ID: {self.cucholix_repo_id}")

    def select_game_file(self):
        """Select game ISO/WBFS file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr.get("select_game_file"),
            "",
            "Game Files (*.iso *.wbfs *.nkit.iso *.iso.dec *.gcm);;All Files (*.*)"
        )
        if file_path:
            self.game_label.setText(Path(file_path).name)
            self.game_label.setStyleSheet("color: #2196F3; font-style: normal;")
            self.game_source_path = file_path
            self.flag_game_specified = True

            # Extract game info
            print(f"Extracting game info from: {file_path}")
            game_info = game_info_extractor.extract_game_info(Path(file_path))

            if game_info:
                self.title_id_hex = game_info.get('title_id', '')
                self.internal_game_name = game_info.get('title', 'Unknown')
                full_game_id = game_info.get('game_id', '')

                # Repository uses only first 4 characters of game ID
                # e.g., RMGE01 -> RMGE
                self.cucholix_repo_id = full_game_id[:4] if len(full_game_id) >= 4 else full_game_id

                # Generate proper hex title ID (ASCII hex encoding)
                # RUUK -> 5255554B
                game_id_4char = full_game_id[:4] if len(full_game_id) >= 4 else full_game_id
                title_id_hex = game_id_4char.encode('ascii').hex().upper()

                # Auto-generate full Title ID based on system type
                system_type = game_info.get('system', 'wii')
                if system_type == 'gc':
                    # GameCube: 00050002 prefix
                    full_title_id = f"00050002{title_id_hex}"
                else:
                    # Wii: 00050000 prefix
                    full_title_id = f"00050000{title_id_hex}"

                # Auto-fill the Title ID field
                self.packed_title_id_line.setText(full_title_id)

                self.game_name_display.setText(f"Name: {self.internal_game_name}")
                self.game_id_display.setText(f"ID: {full_game_id}  |  Title ID: {title_id_hex}")

                # Auto-set title key and game title from DB
                # This will set both title key and game title (Korean name if available)
                self.auto_set_title_key(game_info)

                print(f"Game info extracted successfully:")
                print(f"  - Full Game ID: {full_game_id}")
                print(f"  - Repository ID (first 4 chars): {self.cucholix_repo_id}")
                print(f"  - Title: {self.internal_game_name}")
                print(f"  - Title ID Hex: {title_id_hex}")
                print(f"  - Full Title ID: {full_title_id} (auto-generated)")
            else:
                print("Failed to extract game info!")
                QMessageBox.warning(
                    self,
                    tr.get("game_info_error"),
                    tr.get("game_info_error_msg")
                )
                self.game_name_display.setText(tr.get("internal_name_could_not_read"))
                self.game_id_display.setText(tr.get("title_id_could_not_read"))

    def select_icon_file(self):
        """Select icon image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr.get("select_icon_image"),
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.icon_label.setText(Path(file_path).name)
            self.icon_label.setStyleSheet("color: #2196F3; font-style: normal;")
            self.icon_source_path = file_path
            self.flag_icon_specified = True

            # Process and preview
            if image_processor.process_icon(Path(file_path), paths.temp_icon):
                pixmap = QPixmap(str(paths.temp_icon))
                self.icon_preview.setPixmap(pixmap)

    def select_banner_file(self):
        """Select banner image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr.get("select_banner_image"),
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.banner_label.setText(Path(file_path).name)
            self.banner_label.setStyleSheet("color: #2196F3; font-style: normal;")
            self.banner_source_path = file_path
            self.flag_banner_specified = True

            pixmap = QPixmap(file_path)
            self.banner_preview.setPixmap(pixmap)

    def select_drc_file(self):
        """Select DRC image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr.get("select_drc_image"),
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.drc_label.setText(Path(file_path).name)
            self.drc_label.setStyleSheet("color: #2196F3; font-style: normal;")
            self.drc_source_path = file_path
            self.flag_drc_specified = True

            pixmap = QPixmap(file_path)
            self.drc_preview.setPixmap(pixmap)

    def select_logo_file(self):
        """Select logo image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr.get("select_logo_image"),
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.logo_label.setText(Path(file_path).name)
            self.logo_label.setStyleSheet("color: #2196F3; font-style: normal;")
            self.logo_source_path = file_path
            self.flag_logo_specified = True

            pixmap = QPixmap(file_path)
            self.logo_preview.setPixmap(pixmap)

    def select_boot_sound_file(self):
        """Select boot sound."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr.get("select_boot_sound"),
            "",
            "Audio Files (*.wav);;All Files (*.*)"
        )
        if file_path:
            self.boot_sound_label.setText(Path(file_path).name)
            self.boot_sound_label.setStyleSheet("color: #2196F3; font-style: normal;")
            self.boot_sound_path = file_path
            self.flag_boot_sound_specified = True
            self.boot_sound_preview_btn.setEnabled(True)

    def select_gc2_file(self):
        """Select second GameCube disc."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr.get("select_second_disc"),
            "",
            "Game Files (*.iso *.gcm);;All Files (*.*)"
        )
        if file_path:
            self.gc2_label.setText(Path(file_path).name)
            self.gc2_label.setStyleSheet("color: #2196F3; font-style: normal;")
            self.gc2_source_path = file_path
            self.flag_gc2_specified = True

    def select_main_dol(self):
        """Select custom main.dol."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr.get("select_main_dol"),
            "",
            "DOL Files (*.dol);;All Files (*.*)"
        )
        if file_path:
            self.main_dol_label.setText(Path(file_path).name)
            self.main_dol_label.setStyleSheet("color: #2196F3; font-style: normal;")
            self.main_dol_path = file_path

    def download_from_repo(self):
        """Download images from repository."""
        if not self.cucholix_repo_id:
            QMessageBox.warning(
                self,
                tr.get("no_game_selected"),
                tr.get("no_game_selected_msg")
            )
            return

        # Try to download with alternative IDs
        import urllib.request
        import urllib.error
        import ssl
        from .game_tdb import GameTdb

        # Create SSL context that doesn't verify certificates (for GitHub)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Ensure temp directory exists
        paths.temp_source.mkdir(parents=True, exist_ok=True)

        # Get alternative IDs from GameTDB
        alternative_ids = list(GameTdb.get_alternative_ids(self.cucholix_repo_id))
        print(f"Trying alternative IDs: {alternative_ids}")

        # Try each ID until we find one that works
        for game_id in alternative_ids:
            icon_url = f"{self.repo_url}{self.system_type}/{game_id}/iconTex.png"
            banner_url = f"{self.repo_url}{self.system_type}/{game_id}/bootTvTex.png"

            print(f"Trying ID: {game_id}")
            print(f"  Icon URL: {icon_url}")

            # Check if icon exists (HEAD request)
            try:
                req = urllib.request.Request(
                    icon_url,
                    method='HEAD',
                    headers={'User-Agent': 'WiiVC-Injector/1.0'}
                )
                urllib.request.urlopen(req, context=ssl_context, timeout=5)
                print(f"  ✓ Found! Downloading from {game_id}...")
                break
            except:
                print(f"  ✗ Not found")
                continue
        else:
            # No valid ID found
            QMessageBox.warning(
                self,
                tr.get("images_not_found"),
                tr.get("images_not_found_msg", ids=', '.join(alternative_ids), system=self.system_type),
                QMessageBox.Yes | QMessageBox.No
            )
            return

        # Download from the found ID
        try:
            # Download icon with proper headers
            icon_path = paths.temp_icon
            req = urllib.request.Request(
                icon_url,
                headers={'User-Agent': 'WiiVC-Injector/1.0'}
            )

            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                icon_data = response.read()
                with open(icon_path, 'wb') as f:
                    f.write(icon_data)

            print(f"Icon downloaded: {len(icon_data)} bytes")

            # Download banner
            banner_path = paths.temp_banner
            req = urllib.request.Request(
                banner_url,
                headers={'User-Agent': 'WiiVC-Injector/1.0'}
            )

            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                banner_data = response.read()
                with open(banner_path, 'wb') as f:
                    f.write(banner_data)

            print(f"Banner downloaded: {len(banner_data)} bytes")

            # Update UI
            self.icon_source_path = str(icon_path)
            self.icon_label.setText(f"iconTex.png ({tr.get('from_repo')})")
            self.icon_label.setStyleSheet("color: #4CAF50; font-style: normal;")
            self.flag_icon_specified = True
            pixmap = QPixmap(str(icon_path))
            self.icon_preview.setPixmap(pixmap)

            self.banner_source_path = str(banner_path)
            self.banner_label.setText(f"bootTvTex.png ({tr.get('from_repo')})")
            self.banner_label.setStyleSheet("color: #4CAF50; font-style: normal;")
            self.flag_banner_specified = True
            pixmap = QPixmap(str(banner_path))
            self.banner_preview.setPixmap(pixmap)

            QMessageBox.information(
                self,
                f"{tr.get('download_success')} 🎉",
                tr.get("download_success_msg", id=self.cucholix_repo_id, icon_size=len(icon_data), banner_size=len(banner_data))
            )

        except urllib.error.HTTPError as e:
            if e.code == 404:
                QMessageBox.warning(
                    self,
                    tr.get("not_found"),
                    tr.get("not_found_msg", game_id=self.cucholix_repo_id, system=self.system_type, url=icon_url)
                )
            else:
                QMessageBox.critical(
                    self,
                    tr.get("download_error"),
                    f"HTTP Error {e.code}: {e.reason}\n\n"
                    f"URL: {icon_url}"
                )
        except urllib.error.URLError as e:
            QMessageBox.critical(
                self,
                tr.get("network_error"),
                tr.get("network_error_msg", error=str(e.reason))
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                tr.get("download_error"),
                f"Failed to download images:\n{str(e)}\n\n"
                f"Game ID: {self.cucholix_repo_id}\n"
                f"System: {self.system_type}"
            )
            import traceback
            traceback.print_exc()

    def save_common_key(self):
        """Verify and save common key."""
        try:
            import json
            key = self.wii_u_common_key.text().strip().upper()

            # Validate format (32 hex characters)
            if len(key) != 32 or not all(c in '0123456789ABCDEF' for c in key):
                QMessageBox.critical(self, tr.get("error"), tr.get("common_key_invalid_format"))
                self.wii_u_common_key.setStyleSheet("background-color: #FFCDD2;")
                return

            # Save to JSON settings file
            settings_file = Path.home() / ".wiivc_injector_settings.json"
            settings = {}
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except Exception as e:
                    print(f"Error reading settings: {e}")

            settings['wii_u_common_key'] = key

            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, tr.get("success"), tr.get("common_key_saved"))
            self.wii_u_common_key.setStyleSheet("background-color: #C8E6C9;")

            # Update key status display
            self.update_build_requirements(self.tabs.count() - 1)

        except Exception as e:
            QMessageBox.critical(self, tr.get("error"), f"Failed to save: {e}")
            import traceback
            traceback.print_exc()

    def save_title_key_from_build_tab(self):
        """Verify and save title key from Build tab."""
        try:
            import json
            key = self.title_key_build.text().strip().upper()

            # Validate format (32 hex characters)
            if len(key) != 32 or not all(c in '0123456789ABCDEF' for c in key):
                QMessageBox.critical(self, tr.get("error"), "타이틀 키는 32자리 HEX 문자여야 합니다.\nTitle key must be 32 hex characters.")
                self.title_key_build.setStyleSheet("background-color: #FFCDD2;")
                return

            # Save to JSON settings file
            settings_file = Path.home() / ".wiivc_injector_settings.json"
            settings = {}
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except Exception as e:
                    print(f"Error reading settings: {e}")

            settings['title_key'] = key

            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, tr.get("success"), "타이틀 키 저장 완료!\nTitle Key saved successfully!")
            self.title_key_build.setStyleSheet("background-color: #C8E6C9;")

            # Update key status display
            self.update_build_requirements(self.tabs.count() - 1)

        except Exception as e:
            QMessageBox.critical(self, tr.get("error"), f"Failed to save: {e}")
            import traceback
            traceback.print_exc()

    def update_build_requirements(self, index):
        """Update build requirements display."""
        if index != self.tabs.count() - 1:  # Not on build tab
            return

        # Check source files
        if self.flag_game_specified and self.flag_icon_specified and self.flag_banner_specified:
            self.source_check.setText(f"✓ {tr.get('source_files_ready')}")
            self.source_check.setStyleSheet("color: #4CAF50;")
        else:
            self.source_check.setText(f"⚠ {tr.get('source_files_not_ready')}")
            self.source_check.setStyleSheet("color: #F44336;")

        # Check meta info
        if self.packed_title_line1.text().strip() and len(self.packed_title_id_line.text()) == 16:
            self.meta_check.setText(f"✓ {tr.get('meta_info_ready')}")
            self.meta_check.setStyleSheet("color: #4CAF50;")
        else:
            self.meta_check.setText(f"⚠ {tr.get('meta_info_not_ready')}")
            self.meta_check.setStyleSheet("color: #F44336;")

        # Check keys - 단순히 형식만 체크 (32자리 HEX)
        common_key = self.wii_u_common_key.text().strip().upper()
        title_key_to_check = self.title_key_build.text().strip().upper() if hasattr(self, 'title_key_build') else ""

        common_ok = len(common_key) == 32 and all(c in '0123456789ABCDEF' for c in common_key)
        title_ok = len(title_key_to_check) == 32 and all(c in '0123456789ABCDEF' for c in title_key_to_check)

        if common_ok and title_ok:
            self.keys_check.setText(f"✓ {tr.get('encryption_keys_ready')}")
            self.keys_check.setStyleSheet("color: #4CAF50;")
        else:
            self.keys_check.setText(f"⚠ {tr.get('encryption_keys_not_ready')}")
            self.keys_check.setStyleSheet("color: #F44336;")

    def start_build(self):
        """Start the build process."""
        # Validate
        common_key = self.wii_u_common_key.text().strip()
        # Use title_key_build from Build tab (prioritize Build tab input)
        title_key = self.title_key_build.text().strip() if hasattr(self, 'title_key_build') else self.title_key.text().strip()

        if not self.flag_game_specified:
            QMessageBox.warning(self, tr.get("error"), tr.get("build_error_no_game"))
            return

        if not self.flag_icon_specified or not self.flag_banner_specified:
            QMessageBox.warning(self, tr.get("error"), tr.get("build_error_no_images"))
            return

        if not common_key or not title_key:
            QMessageBox.warning(self, tr.get("error"), tr.get("build_error_no_keys"))
            return

        if not self.packed_title_line1.text().strip():
            QMessageBox.warning(self, tr.get("error"), tr.get("build_error_no_title"))
            return

        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(
            self,
            tr.get("select_output_directory"),
            "",
            QFileDialog.ShowDirsOnly
        )

        if not output_dir:
            return

        # Build options
        options = {
            "disable_passthrough": False,  # Simplified: Always use default behavior
            "lr_patch": self.lr_patch.isChecked(),
        }

        # Disable UI
        self.build_button.setEnabled(False)
        self.tabs.setEnabled(False)

        # Create and start build thread
        self.build_thread = BuildThread(
            game_path=Path(self.game_source_path),
            system_type=self.system_type,
            output_dir=Path(output_dir),
            common_key=common_key,
            title_key=title_key,
            title_name=self.packed_title_line1.text(),
            title_id=self.packed_title_id_line.text(),
            options=options
        )

        # Connect signals
        self.build_thread.progress_updated.connect(self.on_build_progress)
        self.build_thread.build_finished.connect(self.on_build_finished)

        # Start build
        self.build_thread.start()

    def on_build_progress(self, percent, message):
        """Handle build progress update."""
        self.build_progress.setValue(percent)
        self.build_status.setText(message)

    def on_build_finished(self, success, output_dir):
        """Handle build completion."""
        # Re-enable UI
        self.build_button.setEnabled(True)
        self.tabs.setEnabled(True)

        if success:
            QMessageBox.information(
                self,
                f"{tr.get('build_complete')} 🎉",
                tr.get("build_complete_msg", output=output_dir)
            )
        else:
            QMessageBox.critical(
                self,
                tr.get("build_failed"),
                tr.get("build_failed_msg")
            )

    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # Reload keys after settings are saved
            self.load_saved_keys()

    def show_sdcard_dialog(self):
        """Show SD card utilities."""
        dialog = ModernSDCardDialog(self)
        dialog.exec_()

    def show_compatibility_dialog(self):
        """Show game compatibility database."""
        dialog = CompatibilityDialog(self)
        dialog.exec_()

    def auto_set_title_key(self, game_info: dict):
        """
        Automatically set title key based on game compatibility.
        Uses game ID (title ID) for accurate matching.

        Args:
            game_info: Game information dict with 'title', 'game_id', etc.
        """
        game_title = game_info.get('title', '').strip()
        game_id = game_info.get('game_id', '').strip()

        # Map region code to compatibility DB region format
        region_map = {
            'P': 'EUR',
            'E': 'USA',
            'J': 'JAP',
            'K': 'KOR'
        }

        # Get region from game_id (e.g., RMGE01 -> E = USA)
        region_code = game_id[3] if len(game_id) >= 4 else ''
        region = region_map.get(region_code, 'USA')

        print(f"\n=== Auto Title Key Selection ===")
        print(f"Game ID: {game_id}")
        print(f"Game Title: {game_title}")
        print(f"Region: {region}")

        # Search in compatibility DB
        recommended_host = None
        title_key = None
        found_game = None

        # Step 1: Search by game ID (most accurate)
        if game_id:
            found_game = compatibility_db.get_game_by_id(game_id)
            if found_game:
                print(f"✓ Found by Game ID: {found_game['title']}")

        # Step 2: Fallback to title search
        if not found_game and game_title:
            print(f"Game ID not found, searching by title...")
            games = compatibility_db.search_games(game_title, region)
            if games:
                found_game = games[0]
                print(f"✓ Found by title: {found_game['title']}")

                # Learn this mapping for next time
                if game_id:
                    compatibility_db.update_game_id(
                        found_game['title'],
                        found_game['region'],
                        game_id
                    )
                    print(f"📚 Learned: {game_id} = {found_game['title']}")

        # Get title key from recommended host
        if found_game:
            recommended_host = found_game['host_game']
            print(f"Recommended host: {recommended_host}")

            title_key = compatibility_db.get_host_game_title_key(recommended_host)

            if title_key:
                print(f"Title key: {title_key}")
            else:
                print(f"⚠ No title key set for host: {recommended_host}")

            # Auto-set game title from DB (Korean/localized name)
            db_title = found_game['title']
            if db_title:
                # Extract Korean name only (remove English in parentheses)
                # e.g., "타운으로 놀러가요 동물의 숲 (Animal Crossing: City Folk)" -> "타운으로 놀러가요 동물의 숲"
                korean_title = db_title.split('(')[0].strip()
                self.packed_title_line1.setText(korean_title)
                print(f"✓ Auto-set title from DB (Korean): {korean_title}")
            else:
                # DB entry exists but no title, use internal name
                self.packed_title_line1.setText(game_title)
                print(f"✓ Using internal game name: {game_title}")
        else:
            print(f"⚠ Game not found in compatibility DB")
            # Use internal game name only if DB not found
            self.packed_title_line1.setText(game_title)
            print(f"✓ Using internal game name: {game_title}")

        # Default to Rhythm Heaven Fever if not found
        if not title_key:
            recommended_host = "Rhythm Heaven Fever (USA)"
            title_key = compatibility_db.get_host_game_title_key(recommended_host)
            print(f"Using default: {recommended_host}")
            print(f"Default title key: {title_key}")

        # Set the title key in Build tab
        if title_key and hasattr(self, 'title_key_build'):
            self.title_key_build.setText(title_key)
            self.title_key_build.setStyleSheet("background-color: #E8F5E9;")  # Light green
            print(f"✓ Title key auto-set!")

            # Show notification
            self.build_status.setText(f"✓ Auto-set title key for {recommended_host}")

        print("================================\n")

    def on_language_changed(self, index):
        """Handle language change."""
        lang_code = self.language_combo.itemData(index)
        tr.set_language(lang_code)
        self.update_all_texts()

    def update_all_texts(self):
        """Update all UI texts with current language."""
        # Window title
        self.setWindowTitle(tr.get("app_title"))

        # Bottom buttons
        lang_label = self.findChild(QLabel)
        if lang_label and "🌐" in lang_label.text():
            lang_label.setText(f"🌐 {tr.get('language')}:")

        self.settings_btn.setText(f"⚙ {tr.get('settings')}")
        self.sd_card_btn.setText(f"💾 {tr.get('sd_card_utilities')}")

        # Update language combo items (without triggering signal)
        self.language_combo.blockSignals(True)
        self.language_combo.clear()
        for lang_code, lang_name in tr.get_available_languages():
            self.language_combo.addItem(lang_name, lang_code)
        current_index = 0 if tr.current_language == "en" else 1
        self.language_combo.setCurrentIndex(current_index)
        self.language_combo.blockSignals(False)

        # Rebuild tabs to update all text
        self.rebuild_ui()

    def rebuild_ui(self):
        """Rebuild UI with new language."""
        # Store current state
        current_tab_index = self.tabs.currentIndex()

        # Clear tabs
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)

        # Recreate tabs
        self.create_source_tab()
        self.create_images_tab()
        self.create_meta_tab()
        self.create_advanced_tab()
        self.create_build_tab()

        # Restore tab
        self.tabs.setCurrentIndex(current_tab_index)

        # Update requirements if on build tab
        if current_tab_index == self.tabs.count() - 1:
            self.update_build_requirements(current_tab_index)

    def load_saved_keys(self):
        """Load saved encryption keys from settings file."""
        import json
        settings_file = Path.home() / ".wiivc_injector_settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.wii_u_common_key.setText(settings.get('wii_u_common_key', ''))

                    # Load title key to Build tab only
                    title_key_value = settings.get('title_key', '')
                    if hasattr(self, 'title_key_build'):
                        self.title_key_build.setText(title_key_value)

                    if hasattr(self, 'ancast_key'):
                        self.ancast_key.setText(settings.get('ancast_key', ''))
                print(f"Loaded encryption keys from {settings_file}")

                # Update key status display
                self.update_build_requirements(self.tabs.count() - 1)
            except Exception as e:
                print(f"Error loading encryption keys: {e}")

    def closeEvent(self, event):
        """Clean up on close."""
        paths.cleanup_temp()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Set app-wide font (Korean-friendly)
    font = QFont("Malgun Gothic", 9)
    if not font.exactMatch():
        font = QFont("맑은 고딕", 9)
    if not font.exactMatch():
        font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = ModernWiiVCInjector()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
