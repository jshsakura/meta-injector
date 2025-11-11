"""Main window for WiiVC Injector."""
import sys
import os
import shutil
import zipfile
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QRadioButton,
    QTextEdit, QLineEdit, QCheckBox, QFileDialog,
    QProgressBar, QGroupBox, QMessageBox, QApplication
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from .settings_dialog import SettingsDialog
from .sdcard_dialog import SDCardDialog
from .paths import paths
from .resources import resources
from .image_utils import image_processor
from .game_info import game_info_extractor
from .build_engine import BuildEngine


class WiiVCInjectorWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_temp_directories()

        # State variables
        self.system_type = "wii"
        self.title_id_hex = ""
        self.title_id_text = ""
        self.internal_game_name = ""
        self.flag_game_specified = False
        self.flag_icon_specified = False
        self.flag_banner_specified = False
        self.flag_drc_specified = False
        self.flag_logo_specified = False
        self.flag_boot_sound_specified = False
        self.flag_gc2_specified = False

        # Load saved encryption keys
        self.load_saved_keys()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("WiiU Expedition VC Injector (위유 원정대 VC 인젝터) v1.0.0")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # System type selection
        system_layout = QHBoxLayout()
        self.wii_retail_radio = QRadioButton("Wii Retail")
        self.wii_retail_radio.setChecked(True)
        self.wii_homebrew_radio = QRadioButton("Wii Homebrew")
        self.wii_nand_radio = QRadioButton("Wii NAND")
        self.gc_retail_radio = QRadioButton("GC Retail")

        system_layout.addWidget(self.wii_retail_radio)
        system_layout.addWidget(self.wii_homebrew_radio)
        system_layout.addWidget(self.wii_nand_radio)
        system_layout.addWidget(self.gc_retail_radio)
        system_layout.addStretch()

        main_layout.addLayout(system_layout)

        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Create tabs
        self.create_source_files_tab()
        self.create_source_files_tab2()
        self.create_meta_tab()
        self.create_advanced_tab()
        self.create_build_tab()

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        self.settings_button = QPushButton("Settings")
        self.sd_card_button = QPushButton("SD Card Stuff")
        bottom_layout.addWidget(self.settings_button)
        bottom_layout.addWidget(self.sd_card_button)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

        # Connect signals
        self.connect_signals()

    def create_source_files_tab(self):
        """Create the first source files tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Game source
        game_group = QGroupBox("Game ISO/WBFS")
        game_layout = QVBoxLayout()
        self.game_source_button = QPushButton("Select Game...")
        self.game_source_label = QLabel("No file selected")
        game_layout.addWidget(self.game_source_button)
        game_layout.addWidget(self.game_source_label)
        game_group.setLayout(game_layout)
        layout.addWidget(game_group)

        # Icon source
        icon_group = QGroupBox("Icon Image")
        icon_layout = QVBoxLayout()
        self.icon_source_button = QPushButton("Select Icon...")
        self.icon_source_label = QLabel("No file selected")
        self.icon_preview_label = QLabel()
        self.icon_preview_label.setFixedSize(128, 128)
        self.icon_preview_label.setScaledContents(True)
        icon_layout.addWidget(self.icon_source_button)
        icon_layout.addWidget(self.icon_source_label)
        icon_layout.addWidget(self.icon_preview_label)
        icon_group.setLayout(icon_layout)
        layout.addWidget(icon_group)

        # Banner source
        banner_group = QGroupBox("Banner Image")
        banner_layout = QVBoxLayout()
        self.banner_source_button = QPushButton("Select Banner...")
        self.banner_source_label = QLabel("No file selected")
        self.banner_preview_label = QLabel()
        self.banner_preview_label.setFixedSize(256, 128)
        self.banner_preview_label.setScaledContents(True)
        banner_layout.addWidget(self.banner_source_button)
        banner_layout.addWidget(self.banner_source_label)
        banner_layout.addWidget(self.banner_preview_label)
        banner_group.setLayout(banner_layout)
        layout.addWidget(banner_group)

        # Title info
        info_layout = QVBoxLayout()
        self.title_id_info = QLabel("Title ID: ")
        self.game_name_info = QLabel("Game Name: ")
        info_layout.addWidget(self.title_id_info)
        info_layout.addWidget(self.game_name_info)
        layout.addLayout(info_layout)

        # Repo download button
        self.repo_download_button = QPushButton("Download from Repository")
        layout.addWidget(self.repo_download_button)

        layout.addStretch()
        self.tabs.addTab(tab, "Source Files")

    def create_source_files_tab2(self):
        """Create the second source files tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # DRC Image
        drc_group = QGroupBox("DRC (GamePad) Image")
        drc_layout = QVBoxLayout()
        self.drc_source_button = QPushButton("Select DRC Image...")
        self.drc_source_label = QLabel("No file selected")
        self.drc_preview_label = QLabel()
        self.drc_preview_label.setFixedSize(256, 192)
        self.drc_preview_label.setScaledContents(True)
        drc_layout.addWidget(self.drc_source_button)
        drc_layout.addWidget(self.drc_source_label)
        drc_layout.addWidget(self.drc_preview_label)
        drc_group.setLayout(drc_layout)
        layout.addWidget(drc_group)

        # Logo Image
        logo_group = QGroupBox("Logo Image")
        logo_layout = QVBoxLayout()
        self.logo_source_button = QPushButton("Select Logo...")
        self.logo_source_label = QLabel("No file selected")
        self.logo_preview_label = QLabel()
        self.logo_preview_label.setFixedSize(170, 42)
        self.logo_preview_label.setScaledContents(True)
        logo_layout.addWidget(self.logo_source_button)
        logo_layout.addWidget(self.logo_source_label)
        logo_layout.addWidget(self.logo_preview_label)
        logo_group.setLayout(logo_layout)
        layout.addWidget(logo_group)

        # Boot Sound
        sound_group = QGroupBox("Boot Sound")
        sound_layout = QVBoxLayout()
        self.boot_sound_button = QPushButton("Select Boot Sound...")
        self.boot_sound_label = QLabel("No file selected")
        self.boot_sound_preview_button = QPushButton("Preview")
        self.toggle_boot_sound_loop = QCheckBox("Loop Boot Sound")
        sound_layout.addWidget(self.boot_sound_button)
        sound_layout.addWidget(self.boot_sound_label)
        sound_layout.addWidget(self.boot_sound_preview_button)
        sound_layout.addWidget(self.toggle_boot_sound_loop)
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)

        # GC2 Source
        gc2_group = QGroupBox("Second Disc (GC2)")
        gc2_layout = QVBoxLayout()
        self.gc2_source_button = QPushButton("Select GC2...")
        self.gc2_source_label = QLabel("No file selected")
        gc2_layout.addWidget(self.gc2_source_button)
        gc2_layout.addWidget(self.gc2_source_label)
        gc2_group.setLayout(gc2_layout)
        layout.addWidget(gc2_group)

        layout.addStretch()
        self.tabs.addTab(tab, "Source Files 2")

    def create_meta_tab(self):
        """Create the meta information tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Packed Title
        title_group = QGroupBox("Packed Title")
        title_layout = QVBoxLayout()
        self.packed_title_line1 = QLineEdit()
        self.packed_title_line2 = QLineEdit()
        self.enable_packed_line2 = QCheckBox("Enable Line 2")
        title_layout.addWidget(QLabel("Line 1:"))
        title_layout.addWidget(self.packed_title_line1)
        title_layout.addWidget(self.enable_packed_line2)
        title_layout.addWidget(QLabel("Line 2:"))
        title_layout.addWidget(self.packed_title_line2)
        title_group.setLayout(title_layout)
        layout.addWidget(title_group)

        # Packed Title ID
        tid_group = QGroupBox("Packed Title ID")
        tid_layout = QVBoxLayout()
        self.packed_title_id_line = QLineEdit()
        tid_layout.addWidget(self.packed_title_id_line)
        tid_group.setLayout(tid_layout)
        layout.addWidget(tid_group)

        # GamePad Emulation
        gamepad_group = QGroupBox("GamePad Mode")
        gamepad_layout = QVBoxLayout()
        self.no_gamepad_emu = QRadioButton("No Emulation")
        self.no_gamepad_emu.setChecked(True)
        self.cc_emu = QRadioButton("Classic Controller Emulation")
        self.force_cc = QRadioButton("Force Classic Controller")
        self.force_no_cc = QRadioButton("Force No Classic Controller")
        self.hor_wiimote = QRadioButton("Horizontal Wiimote")
        self.ver_wiimote = QRadioButton("Vertical Wiimote")
        gamepad_layout.addWidget(self.no_gamepad_emu)
        gamepad_layout.addWidget(self.cc_emu)
        gamepad_layout.addWidget(self.force_cc)
        gamepad_layout.addWidget(self.force_no_cc)
        gamepad_layout.addWidget(self.hor_wiimote)
        gamepad_layout.addWidget(self.ver_wiimote)
        gamepad_group.setLayout(gamepad_layout)
        layout.addWidget(gamepad_group)

        # LR Patch
        self.lr_patch = QCheckBox("LR Patch")
        layout.addWidget(self.lr_patch)

        layout.addStretch()
        self.tabs.addTab(tab, "Meta")

    def create_advanced_tab(self):
        """Create the advanced options tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Ancast Key
        key_group = QGroupBox("Ancast Key")
        key_layout = QVBoxLayout()
        self.ancast_key = QLineEdit()
        self.save_ancast_key_button = QPushButton("Save Ancast Key")
        key_layout.addWidget(self.ancast_key)
        key_layout.addWidget(self.save_ancast_key_button)
        key_group.setLayout(key_layout)
        layout.addWidget(key_group)

        # C2W Patcher
        self.c2w_patch_flag = QCheckBox("Enable C2W Patcher")
        layout.addWidget(self.c2w_patch_flag)

        # Custom Main DOL
        dol_group = QGroupBox("Custom Main DOL")
        dol_layout = QVBoxLayout()
        self.custom_main_dol = QCheckBox("Use Custom Main DOL")
        self.main_dol_source_button = QPushButton("Select Main DOL...")
        self.main_dol_label = QLabel("No file selected")
        dol_layout.addWidget(self.custom_main_dol)
        dol_layout.addWidget(self.main_dol_source_button)
        dol_layout.addWidget(self.main_dol_label)
        dol_group.setLayout(dol_layout)
        layout.addWidget(dol_group)

        # Various options
        self.force_43_nintendont = QCheckBox("Force 4:3 (Nintendont)")
        self.force_interlaced = QCheckBox("Force Interlaced (Nintendont)")
        self.disable_passthrough = QCheckBox("Disable Passthrough")
        self.force_43_nand = QCheckBox("Force 4:3 (NAND)")
        self.disable_trimming = QCheckBox("Disable Trimming")
        self.disable_nintendont_autoboot = QCheckBox("Disable Nintendont Autoboot")
        self.disable_gamepad = QCheckBox("Disable GamePad")
        self.wii_vmc = QCheckBox("Wii VMC")
        self.wiimmfi = QCheckBox("Wiimmfi")

        layout.addWidget(self.force_43_nintendont)
        layout.addWidget(self.force_interlaced)
        layout.addWidget(self.disable_passthrough)
        layout.addWidget(self.force_43_nand)
        layout.addWidget(self.disable_trimming)
        layout.addWidget(self.disable_nintendont_autoboot)
        layout.addWidget(self.disable_gamepad)
        layout.addWidget(self.wii_vmc)
        layout.addWidget(self.wiimmfi)

        layout.addStretch()
        self.tabs.addTab(tab, "Advanced")

    def create_build_tab(self):
        """Create the build tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Requirements
        req_group = QGroupBox("Requirements")
        req_layout = QVBoxLayout()
        self.source_check = QLabel("❌ Source Files")
        self.meta_check = QLabel("❌ Meta Information")
        self.keys_check = QLabel("❌ Encryption Keys")
        self.advance_check = QLabel("⚠️ Advanced Options")
        req_layout.addWidget(self.source_check)
        req_layout.addWidget(self.meta_check)
        req_layout.addWidget(self.keys_check)
        req_layout.addWidget(self.advance_check)
        req_group.setLayout(req_layout)
        layout.addWidget(req_group)

        # Keys
        keys_group = QGroupBox("Encryption Keys")
        keys_layout = QVBoxLayout()

        common_layout = QHBoxLayout()
        common_layout.addWidget(QLabel("Wii U Common Key:"))
        self.wii_u_common_key = QLineEdit()
        self.save_common_key_button = QPushButton("Save")
        common_layout.addWidget(self.wii_u_common_key)
        common_layout.addWidget(self.save_common_key_button)

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title Key:"))
        self.title_key = QLineEdit()
        self.save_title_key_button = QPushButton("Save")
        title_layout.addWidget(self.title_key)
        title_layout.addWidget(self.save_title_key_button)

        keys_layout.addLayout(common_layout)
        keys_layout.addLayout(title_layout)
        keys_group.setLayout(keys_layout)
        layout.addWidget(keys_group)

        # Build progress
        self.build_progress = QProgressBar()
        self.build_status = QLabel("Ready to build")
        layout.addWidget(self.build_progress)
        layout.addWidget(self.build_status)

        # Build button
        self.build_button = QPushButton("BUILD")
        self.build_button.setMinimumHeight(60)
        self.build_button.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(self.build_button)

        layout.addStretch()
        self.tabs.addTab(tab, "Build")

    def connect_signals(self):
        """Connect UI signals to slots."""
        self.game_source_button.clicked.connect(self.select_game_file)
        self.icon_source_button.clicked.connect(self.select_icon_file)
        self.banner_source_button.clicked.connect(self.select_banner_file)
        self.drc_source_button.clicked.connect(self.select_drc_file)
        self.logo_source_button.clicked.connect(self.select_logo_file)
        self.boot_sound_button.clicked.connect(self.select_boot_sound_file)
        self.gc2_source_button.clicked.connect(self.select_gc2_file)
        self.build_button.clicked.connect(self.start_build)
        self.settings_button.clicked.connect(self.show_settings)
        self.sd_card_button.clicked.connect(self.show_sdcard_dialog)
        self.save_common_key_button.clicked.connect(self.save_keys_to_settings)
        self.save_title_key_button.clicked.connect(self.save_keys_to_settings)
        self.save_ancast_key_button.clicked.connect(self.save_keys_to_settings)

    def init_temp_directories(self):
        """Initialize temporary directories."""
        # Use global path manager
        paths.create_temp_directories()

        # Extract tools to temp directory
        resources.extract_tools(paths.temp_tools)

    def select_game_file(self):
        """Select game ISO/WBFS file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Game File",
            "",
            "Game Files (*.iso *.wbfs *.nkit.iso *.iso.dec *.gcm);;All Files (*.*)"
        )
        if file_path:
            self.game_source_label.setText(file_path)
            self.flag_game_specified = True

            # Extract game info
            game_info = game_info_extractor.extract_game_info(Path(file_path))
            if game_info:
                self.title_id_hex = game_info['title_id']
                self.internal_game_name = game_info['title']
                self.title_id_info.setText(f"Title ID: {game_info['game_id']} ({self.title_id_hex})")
                self.game_name_info.setText(f"Game Name: {game_info['title']}")

    def select_icon_file(self):
        """Select icon image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Icon Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.icon_source_label.setText(file_path)
            self.flag_icon_specified = True

            # Process and show preview
            if image_processor.process_icon(Path(file_path), paths.temp_icon):
                pixmap = QPixmap(str(paths.temp_icon))
                self.icon_preview_label.setPixmap(pixmap)

    def select_banner_file(self):
        """Select banner image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Banner Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.banner_source_label.setText(file_path)
            self.flag_banner_specified = True
            # Show preview
            pixmap = QPixmap(file_path)
            self.banner_preview_label.setPixmap(pixmap)

    def select_drc_file(self):
        """Select DRC image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select DRC Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.drc_source_label.setText(file_path)
            self.flag_drc_specified = True
            pixmap = QPixmap(file_path)
            self.drc_preview_label.setPixmap(pixmap)

    def select_logo_file(self):
        """Select logo image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Logo Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.logo_source_label.setText(file_path)
            self.flag_logo_specified = True
            pixmap = QPixmap(file_path)
            self.logo_preview_label.setPixmap(pixmap)

    def select_boot_sound_file(self):
        """Select boot sound file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Boot Sound",
            "",
            "Audio Files (*.wav *.mp3);;All Files (*.*)"
        )
        if file_path:
            self.boot_sound_label.setText(file_path)
            self.flag_boot_sound_specified = True

    def select_gc2_file(self):
        """Select second GameCube disc."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select GC2 File",
            "",
            "Game Files (*.iso *.gcm);;All Files (*.*)"
        )
        if file_path:
            self.gc2_source_label.setText(file_path)
            self.flag_gc2_specified = True

    def start_build(self):
        """Start the build process."""
        # Get encryption keys
        common_key = self.wii_u_common_key.text().strip()
        title_key = self.title_key.text().strip()

        # Validate inputs
        if not self.flag_game_specified:
            QMessageBox.warning(self, "Error", "Please select a game file first.")
            return

        if not self.flag_icon_specified or not self.flag_banner_specified:
            QMessageBox.warning(self, "Error", "Please select icon and banner images.")
            return

        if not common_key or not title_key:
            QMessageBox.warning(self, "Error", "Please enter encryption keys.")
            return

        if not self.packed_title_line1.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a game title in the Meta tab.")
            return

        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            "",
            QFileDialog.ShowDirsOnly
        )

        if not output_dir:
            return

        # Determine system type
        system_type = "wii"
        if self.wii_homebrew_radio.isChecked():
            system_type = "dol"
        elif self.wii_nand_radio.isChecked():
            system_type = "wiiware"
        elif self.gc_retail_radio.isChecked():
            system_type = "gcn"

        # Build options
        options = {
            "disable_passthrough": self.disable_passthrough.isChecked(),
            "lr_patch": False,  # Add checkbox for this if needed
        }

        # Create build engine
        def progress_callback(percent, message):
            self.build_progress.setValue(percent)
            self.build_status.setText(message)
            QApplication.processEvents()

        engine = BuildEngine(paths, progress_callback)

        # Disable UI during build
        self.build_button.setEnabled(False)
        self.tabs.setEnabled(False)

        # Start build
        success = engine.build(
            game_path=Path(self.game_source_label.text()),
            system_type=system_type,
            output_dir=Path(output_dir),
            common_key=common_key,
            title_key=title_key,
            title_name=self.packed_title_line1.text(),
            title_id=self.packed_title_id_line.text(),
            options=options
        )

        # Re-enable UI
        self.build_button.setEnabled(True)
        self.tabs.setEnabled(True)

        if success:
            QMessageBox.information(
                self,
                "Success",
                f"Build complete!\n\nOutput: {output_dir}\n\n"
                "Install using WUP Installer GX2 with signature patches enabled."
            )
        else:
            QMessageBox.critical(
                self,
                "Build Failed",
                "Build process failed. Check console output for details."
            )

    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            settings = dialog.get_settings()
            # Apply settings - load keys back to main window
            self.wii_u_common_key.setText(settings.get('wii_u_common_key', ''))
            self.title_key.setText(settings.get('title_key', ''))
            self.ancast_key.setText(settings.get('ancast_key', ''))
            print(f"Settings updated: {settings}")

    def show_sdcard_dialog(self):
        """Show SD card utilities dialog."""
        dialog = SDCardDialog(self)
        dialog.exec_()

    def load_saved_keys(self):
        """Load saved encryption keys from settings file."""
        import json
        settings_file = Path.home() / ".wiivc_injector_settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.wii_u_common_key.setText(settings.get('wii_u_common_key', ''))
                    self.title_key.setText(settings.get('title_key', ''))
                    self.ancast_key.setText(settings.get('ancast_key', ''))
                print(f"Loaded encryption keys from {settings_file}")
            except Exception as e:
                print(f"Error loading encryption keys: {e}")

    def save_keys_to_settings(self):
        """Save current encryption keys to settings file."""
        import json
        settings_file = Path.home() / ".wiivc_injector_settings.json"

        # Load existing settings
        settings = {}
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except Exception as e:
                print(f"Error reading settings: {e}")

        # Update keys
        settings['wii_u_common_key'] = self.wii_u_common_key.text()
        settings['title_key'] = self.title_key.text()
        settings['ancast_key'] = self.ancast_key.text()

        # Save
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            QMessageBox.information(
                self,
                "Keys Saved",
                f"Encryption keys saved successfully!\n\nFile: {settings_file}"
            )
            print(f"Saved encryption keys to {settings_file}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save encryption keys:\n{e}"
            )
            print(f"Error saving encryption keys: {e}")

    def closeEvent(self, event):
        """Clean up on close."""
        # Clean up temp directories
        paths.cleanup_temp()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = WiiVCInjectorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
