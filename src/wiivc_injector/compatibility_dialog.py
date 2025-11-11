"""Compatibility database browser dialog."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QTextEdit, QMessageBox, QHeaderView, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .compatibility_db import compatibility_db


class CompatibilityDialog(QDialog):
    """Dialog for browsing game compatibility database."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("게임 호환성 데이터베이스 (Game Compatibility Database)")
        self.setMinimumSize(1000, 700)

        layout = QVBoxLayout(self)

        # Stats
        stats_group = QGroupBox("📊 통계 (Statistics)")
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel()
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 게임 검색 (Search):"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("게임 제목 입력... (Enter game title...)")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)

        search_layout.addWidget(QLabel("지역 (Region):"))
        self.region_combo = QComboBox()
        self.region_combo.addItems(["All", "USA", "EUR", "JAP", "KOR"])
        self.region_combo.currentTextChanged.connect(self.on_search)
        search_layout.addWidget(self.region_combo)

        search_layout.addWidget(QLabel("Host Game:"))
        self.host_combo = QComboBox()
        self.host_combo.addItem("All")
        self.host_combo.currentTextChanged.connect(self.on_search)
        search_layout.addWidget(self.host_combo)

        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Title", "Region", "Game ID", "Host Game", "GamePad", "Status", "Title Key", "Notes"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.table)

        # Details
        details_group = QGroupBox("📝 상세 정보 (Details)")
        details_layout = QVBoxLayout()

        # Game ID input
        gid_layout = QHBoxLayout()
        gid_layout.addWidget(QLabel("Game ID:"))
        self.game_id_input = QLineEdit()
        self.game_id_input.setPlaceholderText("예: RMGE01 (Example: RMGE01)")
        self.game_id_input.setMaxLength(10)
        gid_layout.addWidget(self.game_id_input)
        self.save_gid_btn = QPushButton("💾 저장 (Save)")
        self.save_gid_btn.clicked.connect(self.save_game_id)
        gid_layout.addWidget(self.save_gid_btn)
        details_layout.addLayout(gid_layout)

        # Title Key input
        tk_layout = QHBoxLayout()
        tk_layout.addWidget(QLabel("Title Key:"))
        self.title_key_input = QLineEdit()
        self.title_key_input.setPlaceholderText("32자리 HEX (32 hex characters)")
        self.title_key_input.setMaxLength(32)
        tk_layout.addWidget(self.title_key_input)
        self.save_key_btn = QPushButton("💾 저장 (Save Key)")
        self.save_key_btn.clicked.connect(self.save_title_key)
        tk_layout.addWidget(self.save_key_btn)
        details_layout.addLayout(tk_layout)

        # Notes
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
        self.notes_text.setReadOnly(True)
        details_layout.addWidget(QLabel("호환성 노트 (Compatibility Notes):"))
        details_layout.addWidget(self.notes_text)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Buttons
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 새로고침 (Refresh)")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        self.close_btn = QPushButton("닫기 (Close)")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        # Current selection
        self.current_game = None

    def load_data(self):
        """Load data from database."""
        # Load host games
        self.host_combo.clear()
        self.host_combo.addItem("All")
        for host in compatibility_db.get_host_games():
            self.host_combo.addItem(host)

        # Load stats
        stats = compatibility_db.get_stats()
        self.stats_label.setText(
            f"총 게임: {stats['total_games']} | "
            f"타이틀 키 등록: {stats['games_with_keys']} | "
            f"호스트 게임: {stats['total_hosts']}"
        )

        # Load all games
        self.on_search()

    def on_search(self):
        """Handle search."""
        query = self.search_input.text().strip()
        region = self.region_combo.currentText()
        host = self.host_combo.currentText()

        if region == "All":
            region = None
        if host == "All":
            host = None

        # Search
        if query or region or host:
            if host:
                games = [g for g in compatibility_db.get_games_by_host(host)
                        if (not region or g['region'] == region) and
                           (not query or query.lower() in g['title'].lower())]
            else:
                games = compatibility_db.search_games(query, region)
        else:
            games = compatibility_db.get_all_games()

        # Update table
        self.table.setRowCount(0)
        for game in games:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(game['title']))
            self.table.setItem(row, 1, QTableWidgetItem(game['region']))

            # Game ID with color
            game_id_item = QTableWidgetItem(game['game_id'] or '')
            if game['game_id']:
                game_id_item.setBackground(QColor(200, 230, 201))  # Green if exists
            self.table.setItem(row, 2, game_id_item)

            self.table.setItem(row, 3, QTableWidgetItem(game['host_game']))

            # GamePad compatibility with color
            gamepad_item = QTableWidgetItem(game['gamepad_compatibility'] or '')
            if game['gamepad_compatibility'] == 'Works':
                gamepad_item.setBackground(QColor(200, 230, 201))  # Green
            elif game['gamepad_compatibility'] == "Doesn't work":
                gamepad_item.setBackground(QColor(255, 205, 210))  # Red
            elif game['gamepad_compatibility'] == 'Issues':
                gamepad_item.setBackground(QColor(255, 249, 196))  # Yellow
            self.table.setItem(row, 4, gamepad_item)

            # Status with color
            status_item = QTableWidgetItem(game['status'] or '')
            if game['status'] == 'Works':
                status_item.setBackground(QColor(200, 230, 201))
            elif game['status'] == "Doesn't Work":
                status_item.setBackground(QColor(255, 205, 210))
            elif game['status'] == 'Issues':
                status_item.setBackground(QColor(255, 249, 196))
            self.table.setItem(row, 5, status_item)

            # Title key
            key_item = QTableWidgetItem(game['title_key'] or '')
            if game['title_key']:
                key_item.setBackground(QColor(200, 230, 201))  # Green if exists
            self.table.setItem(row, 6, key_item)

            # Notes (truncated)
            notes = game['notes'] or ''
            if len(notes) > 50:
                notes = notes[:50] + '...'
            self.table.setItem(row, 7, QTableWidgetItem(notes))

        # Auto resize columns
        self.table.resizeColumnsToContents()

    def on_item_double_clicked(self, item):
        """Handle double click on table item."""
        row = item.row()
        title = self.table.item(row, 0).text()
        region = self.table.item(row, 1).text()

        # Load game details
        game = compatibility_db.get_game(title, region)
        if game:
            self.current_game = game
            self.game_id_input.setText(game['game_id'] or '')
            self.title_key_input.setText(game['title_key'] or '')
            self.notes_text.setPlainText(game['notes'] or '')

    def save_game_id(self):
        """Save game ID for current game."""
        if not self.current_game:
            QMessageBox.warning(self, "경고", "게임을 먼저 선택하세요.\nPlease select a game first.")
            return

        game_id = self.game_id_input.text().strip().upper()

        # Save
        try:
            compatibility_db.update_game_id(
                self.current_game['title'],
                self.current_game['region'],
                game_id
            )
            QMessageBox.information(self, "성공", "게임 ID 저장 완료!\nGame ID saved successfully!")
            self.on_search()  # Refresh table
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 실패:\n{e}")

    def save_title_key(self):
        """Save title key for current game."""
        if not self.current_game:
            QMessageBox.warning(self, "경고", "게임을 먼저 선택하세요.\nPlease select a game first.")
            return

        title_key = self.title_key_input.text().strip().upper()

        # Validate
        if title_key and (len(title_key) != 32 or not all(c in '0123456789ABCDEF' for c in title_key)):
            QMessageBox.critical(self, "오류", "타이틀 키는 32자리 HEX 문자여야 합니다.\nTitle key must be 32 hex characters.")
            return

        # Save
        try:
            compatibility_db.update_title_key(
                self.current_game['title'],
                self.current_game['region'],
                title_key
            )
            QMessageBox.information(self, "성공", "타이틀 키 저장 완료!\nTitle key saved successfully!")
            self.on_search()  # Refresh table
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 실패:\n{e}")
