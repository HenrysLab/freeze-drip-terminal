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
    ui_loader.registerCustomWidget(ui.QReceivedForm)
    ui_loader.registerCustomWidget(ui.QMainWindowExt)
    ui_loader.registerCustomWidget(ui.QPopupHookableComboBox)
    ui_loader.registerCustomWidget(ui.QSelectAllOnFocusLineEdit)

    ui_path: pathlib.Path
    with importlib.resources.path(ui, 'received_form.ui') as ui_path:
        ui_file: QFile = QFile(str(ui_path))
        if not ui_file.open(QIODevice.ReadOnly):
            raise RuntimeError(f"Cannot open {ui_path}: {ui_file.errorString()}")
        received_form: ui.QReceivedForm = ui_loader.load(ui_file)
        ui_file.close()
    with importlib.resources.path(ui, 'main_window.ui') as ui_path:
        ui_file: QFile = QFile(str(ui_path))
        if not ui_file.open(QIODevice.ReadOnly):
            raise RuntimeError(f"Cannot open {ui_path}: {ui_file.errorString()}")
        main_window: ui.QMainWindowExt = ui_loader.load(ui_file)
        main_window.setup(received_form)
        ui_file.close()
    main_window.show()
    return app.exec_()
