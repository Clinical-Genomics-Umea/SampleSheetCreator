from PySide6.QtCore import QSettings
from pathlib import Path


class SettingsManager:
    """Create a settings manager for the SuperChess application."""

    def __init__(self):

        self.settings = QSettings("Region Västerbotten", "samplecheater")

    def custom_index_paths(self):
        """Manage loading all the settings."""

        paths = [Path(idx) for idx in self.settings.value("indexes")]

        return paths

    def set_custom_index_paths(self, paths):
        """Manage saving all the settings."""
        paths_str = [str(path) for path in paths]
        self.settings.setValue("indexes", paths_str)

    def custom_application_paths(self):
        """Manage loading all the settings."""
        return self.settings.value("applications")

    def set_application_paths(self, paths):
        """Manage saving all the settings."""
        paths_str = [str(path) for path in paths]
        self.settings.setValue("applications", paths_str)

    def user(self):
        return self.settings.value("user")

    def set_user(self, user):
        self.settings.setValue("user", user)

