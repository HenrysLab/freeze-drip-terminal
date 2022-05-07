import importlib.resources
import logging
import pathlib
import sys

from PySide6.QtCore import QCoreApplication, QFile, QIODevice, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

from . import ui


def main() -> int:
    logging.basicConfig()
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app: QApplication = QApplication(sys.argv)

    ui_loader: QUiLoader = QUiLoader()
    ui_loader.registerCustomWidget(ui.QMainWindowExt)
    ui_loader.registerCustomWidget(ui.QPopupHookableComboBox)
    ui_loader.registerCustomWidget(ui.QSelectAllOnFocusLineEdit)
    main_window_ui: pathlib.Path
    with importlib.resources.path(ui, 'main_window.ui') as main_window_ui:
        main_window_ui_file: QFile = QFile(str(main_window_ui))
        if not main_window_ui_file.open(QIODevice.ReadOnly):
            raise RuntimeError(f"Cannot open {main_window_ui}: {main_window_ui_file.errorString()}")
        main_window: ui.QMainWindowExt = ui_loader.load(main_window_ui_file)
        main_window_ui_file.close()

    main_window.show()
    return app.exec_()
