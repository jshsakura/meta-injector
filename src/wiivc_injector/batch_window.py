"""Batch build window - Simplified UI for mass injection."""
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QLabel, QCheckBox, QFileDialog, QMessageBox, QLineEdit, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .batch_builder import BatchBuilder, BatchBuildJob
from .game_info import game_info_extractor
from .compatibility_db import compatibility_db
from .paths import paths
from .settings_dialog import SettingsDialog


class EditGameDialog(QDialog):
    """Dialog to edit individual game metadata."""

    def __init__(self, job: BatchBuildJob, parent=None):
        super().__init__(parent)
        self.job = job
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("Edit Game Metadata")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Title
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Game Title:"))
        self.title_input = QLineEdit(self.job.title_name)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        # Title ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Title ID:"))
        self.id_input = QLineEdit(self.job.title_id)
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
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
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("Wii VC Injector - Batch Mode")
        self.setGeometry(100, 100, 900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Top controls
        top_layout = QHBoxLayout()

        add_btn = QPushButton("➕ Add Games")
        add_btn.clicked.connect(self.add_games)
        top_layout.addWidget(add_btn)

        remove_btn = QPushButton("➖ Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        top_layout.addWidget(remove_btn)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear_all)
        top_layout.addWidget(clear_btn)

        top_layout.addStretch()

        self.auto_icons_check = QCheckBox("Auto Download Icons")
        self.auto_icons_check.setChecked(True)
        top_layout.addWidget(self.auto_icons_check)

        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.show_settings)
        top_layout.addWidget(settings_btn)

        layout.addLayout(top_layout)

        # Game list table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "File Name", "Game Title", "Title ID", "Icon", "Status", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self.edit_game)
        layout.addWidget(self.table)

        # Progress
        progress_layout = QVBoxLayout()
        self.status_label = QLabel("Ready - Add games to start")
        progress_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        layout.addLayout(progress_layout)

        # Bottom controls
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.build_btn = QPushButton("🚀 Start Batch Build")
        self.build_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.build_btn.clicked.connect(self.start_batch_build)
        self.build_btn.setEnabled(False)
        bottom_layout.addWidget(self.build_btn)

        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_build)
        bottom_layout.addWidget(self.stop_btn)

        layout.addLayout(bottom_layout)

    def add_games(self):
        """Add game files to batch queue."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Game Files",
            "",
            "Game Files (*.iso *.wbfs *.nkit.iso *.iso.dec *.gcm);;All Files (*.*)"
        )

        if not file_paths:
            return

        for file_path in file_paths:
            # Extract game info
            game_path = Path(file_path)
            game_info = game_info_extractor.extract_game_info(game_path)

            if not game_info:
                print(f"Failed to extract info from {game_path.name}")
                continue

            # Create job
            job = BatchBuildJob(game_path, game_info)
            self.prepare_job_metadata(job)
            self.jobs.append(job)

            # Add to table
            self.add_job_to_table(job)

        self.update_ui_state()

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

        # Generate title ID
        game_id_4char = game_id[:4] if len(game_id) >= 4 else game_id
        title_id_hex = game_id_4char.encode('ascii').hex().upper()

        system_type = game_info.get('system', 'wii')
        if system_type == 'gc':
            job.title_id = f"00050002{title_id_hex}"
        else:
            job.title_id = f"00050000{title_id_hex}"

    def add_job_to_table(self, job: BatchBuildJob):
        """Add job to table."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # File name
        self.table.setItem(row, 0, QTableWidgetItem(job.game_path.name))

        # Game title
        self.table.setItem(row, 1, QTableWidgetItem(job.title_name))

        # Title ID
        self.table.setItem(row, 2, QTableWidgetItem(job.title_id))

        # Icon status
        icon_status = "Auto" if self.auto_icons_check.isChecked() else "None"
        self.table.setItem(row, 3, QTableWidgetItem(icon_status))

        # Status
        status_item = QTableWidgetItem("Pending")
        status_item.setBackground(QColor(255, 249, 196))  # Yellow
        self.table.setItem(row, 4, status_item)

        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_game_by_row(row))
        self.table.setCellWidget(row, 5, edit_btn)

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
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Remove all games from the list?",
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
        self.status_label.setText(f"Ready - {len(self.jobs)} game(s) in queue")

    def start_batch_build(self):
        """Start batch building."""
        # Get keys from settings
        import json
        settings_file = Path.home() / ".wiivc_injector_settings.json"

        if not settings_file.exists():
            QMessageBox.warning(self, "Error", "Please configure encryption keys in Settings first!")
            return

        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                common_key = settings.get('wii_u_common_key', '')
                title_key = settings.get('title_key', '')

                if not common_key or not title_key:
                    QMessageBox.warning(self, "Error", "Encryption keys not configured!")
                    return
        except:
            QMessageBox.warning(self, "Error", "Failed to load settings!")
            return

        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
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
        self.batch_builder = BatchBuilder(
            self.jobs,
            common_key,
            title_key,
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
            status_item = self.table.item(idx, 4)
            status_item.setText("Building...")
            status_item.setBackground(QColor(173, 216, 230))  # Light blue

    def on_job_finished(self, idx, success, message):
        """Handle job finished."""
        if idx < self.table.rowCount():
            status_item = self.table.item(idx, 4)
            if success:
                status_item.setText("✓ Completed")
                status_item.setBackground(QColor(200, 230, 201))  # Green
            else:
                status_item.setText(f"✗ Failed: {message}")
                status_item.setBackground(QColor(255, 205, 210))  # Red

    def on_all_finished(self, success_count, total_count):
        """Handle all jobs finished."""
        self.build_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self.status_label.setText(f"Completed: {success_count}/{total_count} succeeded")

        QMessageBox.information(
            self,
            "Batch Build Complete",
            f"Build finished!\n\nSuccess: {success_count}\nFailed: {total_count - success_count}\nTotal: {total_count}"
        )

    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec_()
