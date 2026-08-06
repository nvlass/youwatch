from PySide6.QtCore import QThread, QSize, Signal
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from youwatch import player, search
from youwatch.search import VideoResult
from youwatch.ui.results_model import ResultsModel, WEBPAGE_URL_ROLE


class SearchThread(QThread):
    succeeded = Signal(list)
    failed = Signal(str)

    def __init__(self, query: str, parent=None):
        super().__init__(parent)
        self._query = query

    def run(self) -> None:
        try:
            if search.is_youtube_url(self._query):
                results = search.list_channel(self._query)
            else:
                results = search.search(self._query)
        except Exception as exc:  # yt-dlp raises a variety of errors
            self.failed.emit(str(exc))
            return
        self.succeeded.emit(results)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("youwatch")
        self.resize(640, 480)

        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText(
            "Search YouTube, or paste a channel/playlist URL…"
        )
        self._search_box.returnPressed.connect(self._on_search)

        self._status_label = QLabel("")

        self._results_view = QListView()
        self._results_model = ResultsModel(self)
        self._results_view.setModel(self._results_model)
        self._results_view.setIconSize(QSize(128, 72))
        self._results_view.doubleClicked.connect(self._on_play)

        layout = QVBoxLayout()
        layout.addWidget(self._search_box)
        layout.addWidget(self._status_label)
        layout.addWidget(self._results_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self._search_thread: SearchThread | None = None

    def _on_search(self) -> None:
        query = self._search_box.text().strip()
        if not query:
            return
        self._status_label.setText("Searching…")
        self._search_box.setEnabled(False)
        self._search_thread = SearchThread(query, self)
        self._search_thread.succeeded.connect(self._on_search_succeeded)
        self._search_thread.failed.connect(self._on_search_failed)
        self._search_thread.finished.connect(self._on_search_thread_finished)
        self._search_thread.start()

    def _on_search_thread_finished(self) -> None:
        self._search_box.setEnabled(True)

    def _on_search_succeeded(self, results: list[VideoResult]) -> None:
        self._results_model.set_results(results)
        self._status_label.setText(f"{len(results)} result(s)")

    def _on_search_failed(self, message: str) -> None:
        self._status_label.setText("Search failed")
        QMessageBox.warning(self, "Search failed", message)

    def _on_play(self, index) -> None:
        url = index.data(WEBPAGE_URL_ROLE)
        if not url:
            return
        try:
            player.play(url)
        except Exception as exc:
            QMessageBox.critical(self, "Playback failed", str(exc))
