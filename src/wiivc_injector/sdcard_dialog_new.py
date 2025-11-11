"""Modern SD Card utilities dialog for WiiVC Injector."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QCheckBox, QSpinBox,
    QGroupBox, QDialogButtonBox, QMessageBox, QScrollArea,
    QWidget, QGridLayout
)
from PyQt5.QtCore import Qt
import os
from pathlib import Path
from .translations import tr


class ModernSDCardDialog(QDialog):
    """Modern SD Card utilities dialog with checkboxes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_drive = None
        self.init_ui()
        self.reload_drives()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(tr.get("sd_card_utilities"))
        self.setModal(True)
        self.setMinimumSize(700, 700)

        # Apply modern style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
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
            QPushButton#installButton {
                background-color: #4CAF50;
            }
            QPushButton#installButton:hover {
                background-color: #45a049;
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
            QSpinBox {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: 10pt;
            }
            QSpinBox:focus {
                border: 2px solid #2196F3;
            }
            QCheckBox {
                spacing: 8px;
                padding: 6px;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QLabel {
                font-size: 10pt;
            }
        """)

        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # Drive Selection
        drive_group = QGroupBox(tr.get("sd_card_drive_selection"))
        drive_layout = QVBoxLayout()

        drive_select_layout = QHBoxLayout()
        drive_select_layout.addWidget(QLabel(tr.get("select_drive")))
        self.drive_box = QComboBox()
        self.drive_box.setMinimumWidth(250)
        drive_select_layout.addWidget(self.drive_box, 1)
        self.reload_button = QPushButton(f"🔄 {tr.get('reload_drives')}")
        self.reload_button.clicked.connect(self.reload_drives)
        drive_select_layout.addWidget(self.reload_button)

        drive_layout.addLayout(drive_select_layout)
        drive_group.setLayout(drive_layout)
        scroll_layout.addWidget(drive_group)

        # Nintendont Options
        nintendont_group = QGroupBox(tr.get("nintendont_options"))
        nintendont_layout = QGridLayout()
        nintendont_layout.setSpacing(8)

        # Create checkboxes
        self.memcard_emu = QCheckBox(tr.get("memory_card_emulation"))
        self.memcard_emu.setChecked(True)
        self.force_widescreen = QCheckBox(tr.get("force_widescreen"))
        self.force_progressive = QCheckBox(tr.get("force_progressive"))
        self.auto_boot = QCheckBox(tr.get("auto_boot"))
        self.native_control = QCheckBox(tr.get("native_control"))
        self.triforce_arcade = QCheckBox(tr.get("triforce_arcade_mode"))
        self.wiiu_widescreen = QCheckBox(tr.get("wiiu_widescreen"))
        self.auto_width = QCheckBox(tr.get("auto_width"))
        self.auto_width.setChecked(True)

        # Layout in 2 columns
        nintendont_layout.addWidget(self.memcard_emu, 0, 0)
        nintendont_layout.addWidget(self.force_widescreen, 0, 1)
        nintendont_layout.addWidget(self.force_progressive, 1, 0)
        nintendont_layout.addWidget(self.auto_boot, 1, 1)
        nintendont_layout.addWidget(self.native_control, 2, 0)
        nintendont_layout.addWidget(self.triforce_arcade, 2, 1)
        nintendont_layout.addWidget(self.wiiu_widescreen, 3, 0)
        nintendont_layout.addWidget(self.auto_width, 3, 1)

        nintendont_group.setLayout(nintendont_layout)
        scroll_layout.addWidget(nintendont_group)

        # Memory Card Settings
        memcard_group = QGroupBox(tr.get("memory_card_settings"))
        memcard_layout = QVBoxLayout()

        memcard_size_layout = QHBoxLayout()
        memcard_size_layout.addWidget(QLabel(tr.get("memory_card_blocks")))
        self.memcard_blocks = QComboBox()
        self.memcard_blocks.addItems(["251", "507", "1019", "2043"])
        self.memcard_blocks.setCurrentIndex(0)
        memcard_size_layout.addWidget(self.memcard_blocks)
        memcard_size_layout.addStretch()
        memcard_layout.addLayout(memcard_size_layout)

        self.memcard_multi = QCheckBox(tr.get("multi_game_memory_card"))
        memcard_layout.addWidget(self.memcard_multi)

        memcard_group.setLayout(memcard_layout)
        scroll_layout.addWidget(memcard_group)

        # Video Settings
        video_group = QGroupBox(tr.get("video_settings"))
        video_layout = QVBoxLayout()

        force_layout = QHBoxLayout()
        force_layout.addWidget(QLabel(tr.get("force_video_mode")))
        self.video_force_mode = QComboBox()
        self.video_force_mode.addItems(["None", "PAL50", "PAL60", "NTSC", "MPAL"])
        self.video_force_mode.setCurrentIndex(0)
        force_layout.addWidget(self.video_force_mode)
        video_layout.addLayout(force_layout)

        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel(tr.get("video_type")))
        self.video_type_mode = QComboBox()
        self.video_type_mode.addItems(["Auto", "Progressive", "Interlaced"])
        self.video_type_mode.setCurrentIndex(0)
        type_layout.addWidget(self.video_type_mode)
        video_layout.addLayout(type_layout)

        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel(tr.get("video_width")))
        self.video_width = QSpinBox()
        self.video_width.setRange(640, 1920)
        self.video_width.setValue(720)
        self.video_width.setSuffix(" px")
        self.video_width.setEnabled(False)
        width_layout.addWidget(self.video_width)
        self.width_label = QLabel("(Auto)")
        width_layout.addWidget(self.width_label)
        width_layout.addStretch()
        video_layout.addLayout(width_layout)

        video_group.setLayout(video_layout)
        scroll_layout.addWidget(video_group)

        # Other Settings
        other_group = QGroupBox(tr.get("other_settings"))
        other_layout = QVBoxLayout()

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(tr.get("language")))
        self.language_box = QComboBox()
        self.language_box.addItems([
            "English", "Japanese", "German", "French",
            "Spanish", "Italian", "Dutch"
        ])
        self.language_box.setCurrentIndex(0)
        lang_layout.addWidget(self.language_box)
        other_layout.addLayout(lang_layout)

        gamepad_layout = QHBoxLayout()
        gamepad_layout.addWidget(QLabel(tr.get("wiiu_gamepad_slot")))
        self.wii_u_gamepad_slot = QComboBox()
        self.wii_u_gamepad_slot.addItems(["1", "2", "3", "4"])
        self.wii_u_gamepad_slot.setCurrentIndex(0)
        gamepad_layout.addWidget(self.wii_u_gamepad_slot)
        other_layout.addLayout(gamepad_layout)

        other_group.setLayout(other_layout)
        scroll_layout.addWidget(other_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        # Action Buttons
        action_layout = QHBoxLayout()
        self.install_nintendont_button = QPushButton(f"📦 {tr.get('install_nintendont_to_sd')}")
        self.install_nintendont_button.setObjectName("installButton")
        self.install_nintendont_button.setMinimumHeight(40)
        self.install_nintendont_button.clicked.connect(self.install_nintendont)
        action_layout.addWidget(self.install_nintendont_button)
        main_layout.addLayout(action_layout)

        # Close Button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        # Connect signals
        self.drive_box.currentIndexChanged.connect(self.specify_drive)
        self.memcard_emu.toggled.connect(self.check_options)
        self.auto_width.toggled.connect(self.check_options)

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
                            if volume_name:
                                drives.append(f"{drive_path} ({volume_name})")
                            else:
                                drives.append(drive_path)
                    except:
                        pass
                bitmask >>= 1

            if drives:
                self.drive_box.addItems(drives)
            else:
                self.drive_box.addItem(tr.get("no_removable_drives"))
                self.install_nintendont_button.setEnabled(False)
        else:
            # For Linux/Mac
            QMessageBox.warning(
                self,
                tr.get("platform_warning"),
                tr.get("platform_warning_msg")
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

            return volumeNameBuffer.value if rc else ""
        except:
            return ""

    def specify_drive(self):
        """Update selected drive."""
        current_text = self.drive_box.currentText()
        if current_text and "No removable" not in current_text:
            self.selected_drive = current_text.split()[0]
            self.install_nintendont_button.setEnabled(True)
        else:
            self.selected_drive = None
            self.install_nintendont_button.setEnabled(False)

    def check_options(self):
        """Update UI based on selected options."""
        # Memory card emulation
        memcard_enabled = self.memcard_emu.isChecked()
        self.memcard_blocks.setEnabled(memcard_enabled)
        self.memcard_multi.setEnabled(memcard_enabled)

        # Auto width
        auto_width = self.auto_width.isChecked()
        self.video_width.setEnabled(not auto_width)
        if auto_width:
            self.width_label.setText("(Auto)")
        else:
            self.width_label.setText(f"({self.video_width.value()} px)")

    def install_nintendont(self):
        """Install Nintendont to SD card."""
        if not self.selected_drive:
            QMessageBox.warning(
                self,
                tr.get("no_drive"),
                tr.get("no_drive_msg")
            )
            return

        # Confirm installation
        reply = QMessageBox.question(
            self,
            tr.get("install_nintendont"),
            tr.get("install_nintendont_confirm", drive=self.selected_drive),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        QMessageBox.information(
            self,
            tr.get("not_implemented"),
            tr.get("nintendont_install_preview",
                   drive=self.selected_drive,
                   memcard=self.memcard_emu.isChecked(),
                   widescreen=self.force_widescreen.isChecked(),
                   progressive=self.force_progressive.isChecked(),
                   autoboot=self.auto_boot.isChecked(),
                   native=self.native_control.isChecked(),
                   triforce=self.triforce_arcade.isChecked(),
                   wiiu_wide=self.wiiu_widescreen.isChecked(),
                   auto_width=self.auto_width.isChecked())
        )
