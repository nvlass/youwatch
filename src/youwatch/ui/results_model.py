from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from youwatch.search import VideoResult

WEBPAGE_URL_ROLE = Qt.ItemDataRole.UserRole + 1
RESUME_SECONDS_ROLE = Qt.ItemDataRole.UserRole + 2


def _format_duration(seconds: int | None) -> str:
    if not seconds:
        return "—"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


class ResultsModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._results: list[VideoResult] = []
        self._thumbnails: dict[int, QPixmap] = {}
        self._network = QNetworkAccessManager(self)
        self._replies: list[QNetworkReply] = []

    def set_results(self, results: list[VideoResult]) -> None:
        self.beginResetModel()
        for reply in self._replies:
            reply.abort()
        self._replies.clear()
        self._results = results
        self._thumbnails.clear()
        self.endResetModel()
        for row, result in enumerate(results):
            if result.thumbnail_url:
                self._fetch_thumbnail(row, result.thumbnail_url)

    def _fetch_thumbnail(self, row: int, url: str) -> None:
        reply = self._network.get(QNetworkRequest(url))
        reply.finished.connect(lambda: self._on_thumbnail_loaded(row, reply))
        self._replies.append(reply)

    def _on_thumbnail_loaded(self, row: int, reply: QNetworkReply) -> None:
        if reply in self._replies:
            self._replies.remove(reply)
        if reply.error() == QNetworkReply.NetworkError.NoError:
            pixmap = QPixmap()
            if pixmap.loadFromData(reply.readAll()):
                self._thumbnails[row] = pixmap.scaledToHeight(
                    72, Qt.TransformationMode.SmoothTransformation
                )
                index = self.index(row, 0)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DecorationRole])
        reply.deleteLater()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._results)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        result = self._results[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            duration = _format_duration(result.duration)
            text = f"{result.title}\n{result.uploader}  ·  {duration}"
            if result.resume_seconds:
                text += f"\nResume from {_format_duration(result.resume_seconds)}"
            return text
        if role == Qt.ItemDataRole.DecorationRole:
            return self._thumbnails.get(index.row())
        if role == WEBPAGE_URL_ROLE:
            return result.webpage_url
        if role == RESUME_SECONDS_ROLE:
            return result.resume_seconds
        return None
