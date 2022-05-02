from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLineEdit


class QSelectAllOnFocusLineEdit(QLineEdit):
    def mouseReleaseEvent(self, qmouse_event: QMouseEvent):
        super().mouseReleaseEvent(qmouse_event)
        self.selectAll()
