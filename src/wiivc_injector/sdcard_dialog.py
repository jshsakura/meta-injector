"""SD Card utilities dialog for WiiVC Injector."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QCheckBox, QSpinBox,
    QGroupBox, QListWidget, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt
import os
import shutil
from pathlib import Path


class SDCardDialog(QDialog):
    """SD Card utilities dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_drive = None
        self.init_ui()
        self.reload_drives()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("SD Card Utilities")
        self.setModal(True)
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)

        # Drive Selection
        drive_group = QGroupBox("Drive Selection")
        drive_layout = QVBoxLayout()

        drive_select_layout = QHBoxLayout()
        drive_select_layout.addWidget(QLabel("Select Drive:"))
        self.drive_box = QComboBox()
        drive_select_layout.addWidget(self.drive_box)
        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.reload_drives)
        drive_select_layout.addWidget(self.reload_button)

        drive_layout.addLayout(drive_select_layout)
        drive_group.setLayout(drive_layout)
        layout.addWidget(drive_group)

        # Nintendont Options
        nintendont_group = QGroupBox("Nintendont Options")
        nintendont_layout = QVBoxLayout()

        self.nintendont_options = QListWidget()
        self.nintendont_options.setSelectionMode(QListWidget.MultiSelection)
        options = [
            "Memory Card Emulation",
            "Force Widescreen",
            "Force Progressive",
            "Auto Boot",
            "Native Control",
            "Triforce Arcade Mode",
            "WiiU Widescreen",
            "Auto Width",
        ]
        self.nintendont_options.addItems(options)

        # Set default selections (indices 0 and 7)
        self.nintendont_options.item(0).setSelected(True)
        self.nintendont_options.item(7).setSelected(True)

        nintendont_layout.addWidget(self.nintendont_options)
        nintendont_group.setLayout(nintendont_layout)
        layout.addWidget(nintendont_group)

        # Memory Card Settings
        memcard_group = QGroupBox("Memory Card Settings")
        memcard_layout = QVBoxLayout()

        memcard_size_layout = QHBoxLayout()
        memcard_size_layout.addWidget(QLabel("Memory Card Blocks:"))
        self.memcard_blocks = QComboBox()
        self.memcard_blocks.addItems(["251", "507", "1019", "2043"])
        self.memcard_blocks.setCurrentIndex(0)
        memcard_size_layout.addWidget(self.memcard_blocks)
        memcard_layout.addLayout(memcard_size_layout)

        self.memcard_multi = QCheckBox("Multi-game memory card")
        memcard_layout.addWidget(self.memcard_multi)

        memcard_group.setLayout(memcard_layout)
        layout.addWidget(memcard_group)

        # Video Settings
        video_group = QGroupBox("Video Settings")
        video_layout = QVBoxLayout()

        force_layout = QHBoxLayout()
        force_layout.addWidget(QLabel("Force Video Mode:"))
        self.video_force_mode = QComboBox()
        self.video_force_mode.addItems(["None", "PAL50", "PAL60", "NTSC", "MPAL"])
        self.video_force_mode.setCurrentIndex(0)
        force_layout.addWidget(self.video_force_mode)
        video_layout.addLayout(force_layout)

        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Video Type:"))
        self.video_type_mode = QComboBox()
        self.video_type_mode.addItems(["Auto", "Progressive", "Interlaced"])
        self.video_type_mode.setCurrentIndex(0)
        type_layout.addWidget(self.video_type_mode)
        video_layout.addLayout(type_layout)

        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Video Width:"))
        self.video_width = QSpinBox()
        self.video_width.setRange(640, 1920)
        self.video_width.setValue(720)
        self.video_width.setEnabled(False)
        width_layout.addWidget(self.video_width)
        video_layout.addLayout(width_layout)

        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # Language Settings
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.language_box = QComboBox()
        self.language_box.addItems([
            "English", "Japanese", "German", "French",
            "Spanish", "Italian", "Dutch"
        ])
        self.language_box.setCurrentIndex(0)
        lang_layout.addWidget(self.language_box)
        layout.addLayout(lang_layout)

        # WiiU GamePad Slot
        gamepad_layout = QHBoxLayout()
        gamepad_layout.addWidget(QLabel("WiiU GamePad Slot:"))
        self.wii_u_gamepad_slot = QComboBox()
        self.wii_u_gamepad_slot.addItems(["1", "2", "3", "4"])
        self.wii_u_gamepad_slot.setCurrentIndex(0)
        gamepad_layout.addWidget(self.wii_u_gamepad_slot)
        layout.addLayout(gamepad_layout)

        # Action Buttons
        action_layout = QHBoxLayout()
        self.install_nintendont_button = QPushButton("Install Nintendont to SD")
        self.install_nintendont_button.clicked.connect(self.install_nintendont)
        action_layout.addWidget(self.install_nintendont_button)
        layout.addLayout(action_layout)

        # Close Button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Connect signals
        self.drive_box.currentIndexChanged.connect(self.specify_drive)
        self.nintendont_options.itemSelectionChanged.connect(self.check_options)

    def reload_drives(self):
        """Reload available removable drives."""
        self.drive_box.clear()

        # Get removable drives (Windows-specific logic)
        if os.name == 'nt':
            import string
            from ctypes import windll

            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drive_path = f"{letter}:\\"
                    try:
                        drive_type = windll.kernel32.GetDriveTypeW(drive_path)
                        # DRIVE_REMOVABLE = 2
                        if drive_type == 2:
                            volume_name = self.get_volume_name(drive_path)
                            drives.append(f"{drive_path} ({volume_name})")
                    except:
                        pass
                bitmask >>= 1

            self.drive_box.addItems(drives)
        else:
            # For Linux/Mac, use /media or /Volumes
            QMessageBox.warning(
                self,
                "Platform",
                "SD Card detection is currently Windows-only."
            )

    def get_volume_name(self, drive_path):
        """Get volume name for a drive."""
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            volumeNameBuffer = ctypes.create_unicode_buffer(1024)
            fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
            serial_number = None
            max_component_length = None
            file_system_flags = None

            rc = kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(drive_path),
                volumeNameBuffer,
                ctypes.sizeof(volumeNameBuffer),
                serial_number,
                max_component_length,
                file_system_flags,
                fileSystemNameBuffer,
                ctypes.sizeof(fileSystemNameBuffer)
            )

            return volumeNameBuffer.value if rc else "Unknown"
        except:
            return "Unknown"

    def specify_drive(self):
        """Update selected drive."""
        current_text = self.drive_box.currentText()
        if current_text:
            self.selected_drive = current_text.split()[0]
        else:
            self.selected_drive = None

    def check_options(self):
        """Update UI based on selected options."""
        # Memory card emulation (index 0)
        memcard_enabled = self.nintendont_options.item(0).isSelected()
        self.memcard_blocks.setEnabled(memcard_enabled)
        self.memcard_multi.setEnabled(memcard_enabled)

        # Auto width (index 7)
        auto_width = self.nintendont_options.item(7).isSelected()
        self.video_width.setEnabled(not auto_width)

    def install_nintendont(self):
        """Install Nintendont to SD card."""
        if not self.selected_drive:
            QMessageBox.warning(
                self,
                "No Drive",
                "Please select a drive first."
            )
            return

        QMessageBox.information(
            self,
            "Install Nintendont",
            f"Nintendont installation to {self.selected_drive} would happen here.\n"
            "This feature requires downloading and copying Nintendont files."
        )
