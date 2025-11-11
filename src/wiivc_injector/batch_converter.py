"""Batch WBFS Converter - Convert multiple WBFS files at once."""
import sys
import os
from pathlib import Path
from typing import List
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QComboBox,
    QFileDialog, QProgressBar, QMessageBox, QApplication,
    QGroupBox, QCheckBox, QTextEdit, QListWidgetItem, QSplitter,
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
from .translations import tr
from .game_info import game_info_extractor
import io


class ConversionWorker(QThread):
    """Worker thread for batch conversion."""

    progress = pyqtSignal(int, str)  # percent, message
    file_complete = pyqtSignal(str, bool, str)  # filename, success, message
    all_complete = pyqtSignal(int, int)  # success_count, fail_count

    def __init__(self, files, output_format, output_dir, options):
        super().__init__()
        self.files = files
        self.output_format = output_format
        self.output_dir = output_dir
        self.options = options
        self.is_running = True

    def run(self):
        """Run batch conversion."""
        success_count = 0
        fail_count = 0
        total = len(self.files)

        for idx, file_path in enumerate(self.files):
            if not self.is_running:
                break

            filename = Path(file_path).name
            self.progress.emit(
                int((idx / total) * 100),
                f"Converting {idx + 1}/{total}: {filename}"
            )

            try:
                success = self.convert_file(file_path)
                if success:
                    success_count += 1
                    self.file_complete.emit(filename, True, "✓ Success")
                else:
                    fail_count += 1
                    self.file_complete.emit(filename, False, "✗ Failed")
            except Exception as e:
                fail_count += 1
                self.file_complete.emit(filename, False, f"✗ Error: {str(e)}")

        self.progress.emit(100, f"Complete: {success_count} succeeded, {fail_count} failed")
        self.all_complete.emit(success_count, fail_count)

    def convert_file(self, file_path: str) -> bool:
        """
        Convert a single WBFS file.

        TODO: Implement actual conversion logic using wit or other tools.
        For now, this is a placeholder.
        """
        import time
        time.sleep(0.5)  # Simulate conversion time

        # TODO: Implement actual conversion
        # Example using wit (Wiimms ISO Tools):
        # wit convert input.wbfs output.iso

        return True

    def stop(self):
        """Stop the conversion process."""
        self.is_running = False


class BatchConverterWindow(QMainWindow):
    """Batch WBFS Converter main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr.get("batch_converter_title"))
        self.setGeometry(100, 100, 1000, 650)
        self.setMinimumSize(900, 600)

        self.files = []
        self.file_info_cache = {}  # Cache game info for each file
        self.worker = None

        self.setup_style()
        self.init_ui()

    def setup_style(self):
        """Setup modern styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
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
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QPushButton#convertButton {
                background-color: #4CAF50;
                font-size: 14pt;
                padding: 12px 24px;
            }
            QPushButton#convertButton:hover {
                background-color: #45a049;
            }
            QPushButton#removeButton {
                background-color: #f44336;
            }
            QPushButton#removeButton:hover {
                background-color: #da190b;
            }
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                font-size: 10pt;
            }
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: 10pt;
            }
            QLabel {
                font-size: 10pt;
                color: #333333;
            }
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                background-color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }
        """)

    def init_ui(self):
        """Initialize the UI."""
        # Main scroll area for entire content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        central = QWidget()
        scroll_area.setWidget(central)
        self.setCentralWidget(scroll_area)

        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header = QLabel(f"📦 {tr.get('batch_converter_header')}")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #1976D2; padding: 10px;")
        layout.addWidget(header)

        # File list and preview splitter
        files_group = QGroupBox(tr.get("selected_files"))
        files_main_layout = QVBoxLayout()

        # Create splitter for list and preview
        splitter = QSplitter(Qt.Horizontal)

        # Left side: File list
        left_widget = QWidget()
        files_layout = QVBoxLayout(left_widget)
        files_layout.setContentsMargins(0, 0, 0, 0)

        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(150)
        self.file_list.setMaximumHeight(250)
        self.file_list.setIconSize(QSize(32, 32))
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        files_layout.addWidget(self.file_list)

        # File buttons
        file_buttons = QHBoxLayout()
        self.add_files_btn = QPushButton(f"➕ {tr.get('add_files')}")
        self.remove_files_btn = QPushButton(f"➖ {tr.get('remove_selected')}")
        self.remove_files_btn.setObjectName("removeButton")
        self.clear_files_btn = QPushButton(f"🗑 {tr.get('clear_all')}")
        self.clear_files_btn.setObjectName("removeButton")

        self.add_files_btn.clicked.connect(self.add_files)
        self.remove_files_btn.clicked.connect(self.remove_selected)
        self.clear_files_btn.clicked.connect(self.clear_all)

        file_buttons.addWidget(self.add_files_btn)
        file_buttons.addWidget(self.remove_files_btn)
        file_buttons.addWidget(self.clear_files_btn)
        file_buttons.addStretch()

        self.file_count_label = QLabel(tr.get("files_selected", count=0))
        file_buttons.addWidget(self.file_count_label)

        files_layout.addLayout(file_buttons)

        # Right side: Preview panel
        right_widget = QFrame()
        right_widget.setFrameShape(QFrame.StyledPanel)
        right_widget.setMinimumWidth(250)
        right_widget.setMaximumWidth(350)
        preview_layout = QVBoxLayout(right_widget)

        preview_header = QLabel(f"📋 {tr.get('file_preview')}")
        preview_header.setStyleSheet("font-weight: bold; font-size: 11pt; padding: 5px;")
        preview_layout.addWidget(preview_header)

        # Preview content
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_content = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_content)

        # Default "no selection" message
        self.no_selection_label = QLabel(tr.get("select_file_to_preview"))
        self.no_selection_label.setAlignment(Qt.AlignCenter)
        self.no_selection_label.setStyleSheet("color: #999; padding: 50px;")
        self.preview_layout.addWidget(self.no_selection_label)

        # Preview widgets (hidden initially)
        self.preview_game_title = QLabel()
        self.preview_game_title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        self.preview_game_title.setWordWrap(True)
        self.preview_game_title.hide()

        self.preview_game_id = QLabel()
        self.preview_game_id.setStyleSheet("color: #666;")
        self.preview_game_id.hide()

        self.preview_system = QLabel()
        self.preview_system.hide()

        self.preview_file_type = QLabel()
        self.preview_file_type.hide()

        self.preview_file_size = QLabel()
        self.preview_file_size.hide()

        self.preview_file_path = QLabel()
        self.preview_file_path.setWordWrap(True)
        self.preview_file_path.setStyleSheet("color: #666; font-size: 9pt;")
        self.preview_file_path.hide()

        self.preview_layout.addWidget(self.preview_game_title)
        self.preview_layout.addWidget(self.preview_game_id)
        self.preview_layout.addSpacing(10)
        self.preview_layout.addWidget(self.preview_system)
        self.preview_layout.addWidget(self.preview_file_type)
        self.preview_layout.addWidget(self.preview_file_size)
        self.preview_layout.addSpacing(10)
        self.preview_layout.addWidget(self.preview_file_path)
        self.preview_layout.addStretch()

        self.preview_scroll.setWidget(self.preview_content)
        preview_layout.addWidget(self.preview_scroll)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        files_main_layout.addWidget(splitter)
        files_group.setLayout(files_main_layout)
        layout.addWidget(files_group)

        # Conversion options
        options_group = QGroupBox(tr.get("conversion_options"))
        options_layout = QVBoxLayout()

        # Output format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(tr.get("output_format")))
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "ISO (Standard)",
            "WBFS (Compressed)",
            "NKIT (Compressed)"
        ])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)

        # Output directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel(tr.get("output_directory")))
        self.output_dir_label = QLabel(tr.get("same_as_source"))
        self.output_dir_label.setStyleSheet("color: #666; font-style: italic;")
        self.output_dir_btn = QPushButton(tr.get("browse"))
        self.output_dir_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_dir_label, 1)
        output_layout.addWidget(self.output_dir_btn)
        options_layout.addLayout(output_layout)

        # Options checkboxes
        self.verify_after_conversion = QCheckBox(tr.get("verify_after_conversion"))
        self.delete_source_after = QCheckBox(tr.get("delete_source_after"))
        options_layout.addWidget(self.verify_after_conversion)
        options_layout.addWidget(self.delete_source_after)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress
        progress_group = QGroupBox(tr.get("conversion_progress"))
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setMaximumHeight(30)
        self.progress_label = QLabel(tr.get("ready_to_convert"))
        self.progress_label.setAlignment(Qt.AlignCenter)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Log
        log_group = QGroupBox(tr.get("conversion_log"))
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        self.log_text.setMaximumHeight(120)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Convert button
        self.convert_btn = QPushButton(f"🚀 {tr.get('start_conversion')}")
        self.convert_btn.setObjectName("convertButton")
        self.convert_btn.setMinimumHeight(45)
        self.convert_btn.setMaximumHeight(55)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_btn)

        # Bottom bar
        bottom_bar = QHBoxLayout()

        lang_label = QLabel(f"🌐 {tr.get('language')}:")
        bottom_bar.addWidget(lang_label)

        self.language_combo = QComboBox()
        self.language_combo.setMinimumWidth(100)
        for lang_code, lang_name in tr.get_available_languages():
            self.language_combo.addItem(lang_name, lang_code)
        current_index = 0 if tr.current_language == "en" else 1
        self.language_combo.setCurrentIndex(current_index)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        bottom_bar.addWidget(self.language_combo)

        bottom_bar.addStretch()
        layout.addLayout(bottom_bar)

    def add_files(self):
        """Add WBFS/ISO files to the list."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            tr.get("select_files_to_convert"),
            "",
            "Game Files (*.wbfs *.iso *.nkit.iso *.gcm);;All Files (*.*)"
        )

        if files:
            for file_path in files:
                if file_path not in self.files:
                    self.files.append(file_path)

                    # Extract and cache game info
                    self.log(f"Loading: {Path(file_path).name}...")
                    info = game_info_extractor.extract_game_info(Path(file_path))
                    self.file_info_cache[file_path] = info

                    # Create list item with icon
                    if info:
                        item_text = f"{info.get('title', 'Unknown')}\n{info.get('game_id', 'N/A')} - {Path(file_path).name}"
                    else:
                        item_text = f"Unknown\n{Path(file_path).name}"

                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, file_path)

                    # Set icon based on system type
                    if info:
                        system = info.get('system', 'unknown')
                        if system == 'wii':
                            item.setIcon(self.style().standardIcon(self.style().SP_DriveNetIcon))
                        elif system == 'gc':
                            item.setIcon(self.style().standardIcon(self.style().SP_DriveDVDIcon))
                        else:
                            item.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
                    else:
                        item.setIcon(self.style().standardIcon(self.style().SP_FileIcon))

                    self.file_list.addItem(item)

            self.update_file_count()
            self.log(f"Added {len(files)} file(s)")

    def on_file_selected(self, current, previous):
        """Handle file selection change."""
        if not current:
            # No selection, hide preview
            self.no_selection_label.show()
            self.preview_game_title.hide()
            self.preview_game_id.hide()
            self.preview_system.hide()
            self.preview_file_type.hide()
            self.preview_file_size.hide()
            self.preview_file_path.hide()
            return

        file_path = current.data(Qt.UserRole)
        info = self.file_info_cache.get(file_path)

        # Hide "no selection" message
        self.no_selection_label.hide()

        # Show preview widgets
        if info:
            self.preview_game_title.setText(f"🎮 {info.get('title', 'Unknown')}")
            self.preview_game_title.show()

            self.preview_game_id.setText(f"Game ID: {info.get('game_id', 'N/A')}")
            self.preview_game_id.show()

            system = info.get('system', 'unknown')
            system_map = {'wii': 'Wii', 'gc': 'GameCube', 'unknown': 'Unknown'}
            self.preview_system.setText(f"System: {system_map.get(system, 'Unknown')}")
            self.preview_system.show()

            file_type = info.get('file_type', 'unknown')
            self.preview_file_type.setText(f"Format: {file_type.upper()}")
            self.preview_file_type.show()

            file_size = info.get('file_size', 0)
            size_mb = file_size / (1024 * 1024)
            size_gb = file_size / (1024 * 1024 * 1024)
            if size_gb >= 1:
                size_str = f"{size_gb:.2f} GB"
            else:
                size_str = f"{size_mb:.2f} MB"
            self.preview_file_size.setText(f"Size: {size_str}")
            self.preview_file_size.show()

            self.preview_file_path.setText(f"Path: {file_path}")
            self.preview_file_path.show()
        else:
            self.preview_game_title.setText(f"❓ {Path(file_path).name}")
            self.preview_game_title.show()

            self.preview_game_id.setText("Unable to read game information")
            self.preview_game_id.show()

            self.preview_system.hide()
            self.preview_file_type.hide()
            self.preview_file_size.hide()

            self.preview_file_path.setText(f"Path: {file_path}")
            self.preview_file_path.show()

    def remove_selected(self):
        """Remove selected files from the list."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            if file_path in self.files:
                self.files.remove(file_path)
                if file_path in self.file_info_cache:
                    del self.file_info_cache[file_path]
            self.file_list.takeItem(self.file_list.row(item))

        self.update_file_count()
        self.log(f"Removed {len(selected_items)} file(s)")

    def clear_all(self):
        """Clear all files from the list."""
        if not self.files:
            return

        reply = QMessageBox.question(
            self,
            tr.get("confirm"),
            tr.get("clear_all_confirm"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            count = len(self.files)
            self.files.clear()
            self.file_list.clear()
            self.update_file_count()
            self.log(f"Cleared all {count} file(s)")

    def update_file_count(self):
        """Update the file count label."""
        count = len(self.files)
        self.file_count_label.setText(tr.get("files_selected", count=count))
        self.convert_btn.setEnabled(count > 0)

    def select_output_dir(self):
        """Select output directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            tr.get("select_output_directory"),
            "",
            QFileDialog.ShowDirsOnly
        )

        if directory:
            self.output_dir_label.setText(directory)
            self.output_dir_label.setStyleSheet("color: #2196F3; font-style: normal;")
            self.log(f"Output directory: {directory}")

    def start_conversion(self):
        """Start the batch conversion."""
        if not self.files:
            return

        # Get output directory
        output_dir = self.output_dir_label.text()
        if output_dir == tr.get("same_as_source"):
            output_dir = None

        # Get format
        format_idx = self.format_combo.currentIndex()
        formats = ["iso", "wbfs", "nkit"]
        output_format = formats[format_idx]

        # Options
        options = {
            "verify": self.verify_after_conversion.isChecked(),
            "delete_source": self.delete_source_after.isChecked()
        }

        # Confirm if delete source is enabled
        if options["delete_source"]:
            reply = QMessageBox.warning(
                self,
                tr.get("warning"),
                tr.get("delete_source_warning"),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Disable UI
        self.convert_btn.setEnabled(False)
        self.add_files_btn.setEnabled(False)
        self.remove_files_btn.setEnabled(False)
        self.clear_files_btn.setEnabled(False)

        # Clear log
        self.log_text.clear()
        self.log(f"Starting batch conversion of {len(self.files)} file(s)...")
        self.log(f"Output format: {output_format.upper()}")
        if output_dir:
            self.log(f"Output directory: {output_dir}")
        else:
            self.log("Output directory: Same as source")

        # Start worker
        self.worker = ConversionWorker(self.files, output_format, output_dir, options)
        self.worker.progress.connect(self.on_progress)
        self.worker.file_complete.connect(self.on_file_complete)
        self.worker.all_complete.connect(self.on_all_complete)
        self.worker.start()

    def on_progress(self, percent, message):
        """Update progress."""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)

    def on_file_complete(self, filename, success, message):
        """Log file completion."""
        if success:
            self.log(f"✓ {filename}: {message}", color="green")
        else:
            self.log(f"✗ {filename}: {message}", color="red")

    def on_all_complete(self, success_count, fail_count):
        """Handle completion of all conversions."""
        # Re-enable UI
        self.convert_btn.setEnabled(True)
        self.add_files_btn.setEnabled(True)
        self.remove_files_btn.setEnabled(True)
        self.clear_files_btn.setEnabled(True)

        # Show result
        self.log(f"\n{'='*60}")
        self.log(f"Conversion complete!")
        self.log(f"  Success: {success_count}")
        self.log(f"  Failed: {fail_count}")

        QMessageBox.information(
            self,
            tr.get("conversion_complete"),
            tr.get("conversion_complete_msg", success=success_count, failed=fail_count)
        )

    def log(self, message, color=None):
        """Add message to log."""
        if color:
            color_map = {
                "green": "#4CAF50",
                "red": "#f44336",
                "blue": "#2196F3"
            }
            self.log_text.append(f'<span style="color: {color_map.get(color, "black")};">{message}</span>')
        else:
            self.log_text.append(message)

    def on_language_changed(self, index):
        """Handle language change."""
        lang_code = self.language_combo.itemData(index)
        tr.set_language(lang_code)

        # Show message that app needs restart for full translation
        QMessageBox.information(
            self,
            "Language Changed",
            "Language has been changed. Please restart the application for full effect."
        )

    def closeEvent(self, event):
        """Handle window close."""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                tr.get("confirm"),
                tr.get("conversion_in_progress"),
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Run the batch converter."""
    app = QApplication(sys.argv)

    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = BatchConverterWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
