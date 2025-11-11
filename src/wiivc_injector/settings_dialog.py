"""Settings dialog for WiiVC Injector."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import json
import os
from pathlib import Path


class SettingsDialog(QDialog):
    """Settings dialog window."""

    SETTINGS_FILE = Path.home() / ".wiivc_injector_settings.json"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Banners Repository
        repo_layout = QHBoxLayout()
        repo_layout.addWidget(QLabel("Banners Repository:"))
        self.banners_repository = QLineEdit()
        repo_layout.addWidget(self.banners_repository)
        layout.addLayout(repo_layout)

        # Output Directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.output_dir = QLineEdit()
        self.output_dir_button = QPushButton("Browse...")
        self.output_dir_button.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_dir)
        output_layout.addWidget(self.output_dir_button)
        layout.addLayout(output_layout)

        # Wii U Common Key
        common_key_layout = QHBoxLayout()
        common_key_layout.addWidget(QLabel("Wii U Common Key:"))
        self.wii_u_common_key = QLineEdit()
        self.wii_u_common_key.setPlaceholderText("Enter Wii U Common Key")
        common_key_layout.addWidget(self.wii_u_common_key)
        layout.addLayout(common_key_layout)

        # Title Key
        title_key_layout = QHBoxLayout()
        title_key_layout.addWidget(QLabel("Title Key:"))
        self.title_key = QLineEdit()
        self.title_key.setPlaceholderText("Enter Title Key")
        title_key_layout.addWidget(self.title_key)
        layout.addLayout(title_key_layout)

        # Ancast Key
        ancast_key_layout = QHBoxLayout()
        ancast_key_layout.addWidget(QLabel("Ancast Key:"))
        self.ancast_key = QLineEdit()
        self.ancast_key.setPlaceholderText("Enter Ancast Key (optional)")
        ancast_key_layout.addWidget(self.ancast_key)
        layout.addLayout(ancast_key_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_output_dir(self):
        """Select output directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_dir.text() or str(Path.home())
        )
        if directory:
            self.output_dir.setText(directory)

    def load_settings(self):
        """Load settings from file."""
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.banners_repository.setText(
                        settings.get('banners_repository', '')
                    )
                    self.output_dir.setText(
                        settings.get('output_dir', str(Path.home() / 'Desktop'))
                    )
                    self.wii_u_common_key.setText(
                        settings.get('wii_u_common_key', '')
                    )
                    self.title_key.setText(
                        settings.get('title_key', '')
                    )
                    self.ancast_key.setText(
                        settings.get('ancast_key', '')
                    )
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save settings to file."""
        settings = {
            'banners_repository': self.banners_repository.text(),
            'output_dir': self.output_dir.text(),
            'wii_u_common_key': self.wii_u_common_key.text(),
            'title_key': self.title_key.text(),
            'ancast_key': self.ancast_key.text(),
        }
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"Settings saved successfully to {self.SETTINGS_FILE}")
        except Exception as e:
            print(f"Error saving settings: {e}")
            import traceback
            traceback.print_exc()

    def accept(self):
        """Accept and save settings."""
        self.save_settings()
        super().accept()

    def get_settings(self):
        """Get current settings as dict."""
        return {
            'banners_repository': self.banners_repository.text(),
            'output_dir': self.output_dir.text(),
            'wii_u_common_key': self.wii_u_common_key.text(),
            'title_key': self.title_key.text(),
            'ancast_key': self.ancast_key.text(),
        }
