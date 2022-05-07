from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox


class QPopupHookableComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_show_popup_listeners: list[Callable[['QPopupHookableComboBox'], None]] = list()
        self.on_showed_popup_listeners: list[Callable[['QPopupHookableComboBox'], None]] = list()
        self.on_hide_popup_listeners: list[Callable[['QPopupHookableComboBox'], None]] = list()
        self.on_hid_popup_listeners: list[Callable[['QPopupHookableComboBox'], None]] = list()

    def add_on_show_popup_listener(self, listener: Callable[['QPopupHookableComboBox'], None]):
        self.on_show_popup_listeners.append(listener)

    def remove_on_show_popup_listener(self, listener: Callable[['QPopupHookableComboBox'], None]):
        self.on_show_popup_listeners.remove(listener)

    def add_on_showed_popup_listener(self, listener: Callable[['QPopupHookableComboBox'], None]):
        self.on_showed_popup_listeners.append(listener)

    def remove_on_showed_popup_listener(self, listener: Callable[['QPopupHookableComboBox'], None]):
        self.on_showed_popup_listeners.remove(listener)

    def add_on_hide_popup_listener(self, listener: Callable[['QPopupHookableComboBox'], None]):
        self.on_hide_popup_listeners.append(listener)

    def remove_on_hide_popup_listener(self, listener: Callable[['QPopupHookableComboBox'], None]):
        self.on_hide_popup_listeners.remove(listener)

    def add_on_hid_popup_listener(self, listener: Callable[['QPopupHookableComboBox'], None]):
        self.on_hid_popup_listeners.append(listener)

    def remove_on_hid_popup_listener(self, listener: Callable[['QPopupHookableComboBox'], None]):
        self.on_hid_popup_listeners.remove(listener)

    def showPopup(self):
        last_text = self.currentText()

        listener: Callable[['QPopupHookableComboBox'], None]
        for listener in self.on_show_popup_listeners:
            try:
                listener(self)
            except Exception:
                pass

        if self.count():
            index = self.findText(last_text, flags=Qt.MatchExactly)
            self.setCurrentIndex(0 if index < 0 else index)

        super().showPopup()

        listener: Callable[['QPopupHookableComboBox'], None]
        for listener in self.on_showed_popup_listeners:
            try:
                listener(self)
            except Exception:
                pass

    def hidePopup(self):
        super().hidePopup()
