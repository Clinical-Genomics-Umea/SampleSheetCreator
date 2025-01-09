from models.configuration.configuration_manager import ConfigurationManager


class ApplicationManager:

    def __init__(self, config_manager: ConfigurationManager) -> None:
        """Initialize the application manager."""

        self._app_objects = config_manager.application_configs

        for app_object in self._app_objects:
            app_name = app_object.get("ApplicationName")
            app_type = app_object.get("ApplicationType")
            app = app_object.get("Application")

            if not all([app_name, app_type, app]):
                continue

    def app_name_to_app(self, app_name):

        for app_obj in self._app_objects:
            if app_name == app_obj["ApplicationName"]:
                return app_obj["Application"]

        return None

    def app_to_app_type(self, app):
        for app_obj in self._app_objects:
            if app == app_obj["Application"]:
                return app_obj["ApplicationType"]

    @property
    def app_hierarchy(self):
        _type_to_name_to_obj = {}

        for obj in self._app_objects:
            print(obj)
            a_type = obj["ApplicationType"]
            a_name = obj["ApplicationName"]

            if a_type not in _type_to_name_to_obj:
                _type_to_name_to_obj[a_type] = {}

            _type_to_name_to_obj[a_type][a_name] = obj

        return _type_to_name_to_obj

    def app_name_to_settings(self, app_name):
        for app_obj in self._app_objects:
            if app_name == app_obj["ApplicationName"]:
                return app_obj["Settings"]

        return None

    def app_name_to_data(self, app_name):
        for app_obj in self._app_objects:
            if app_name == app_obj["ApplicationName"]:
                return app_obj["Data"]

        return None

    def app_name_to_data_fields(self, app_name):
        for app_obj in self._app_objects:
            if app_name == app_obj["ApplicationName"]:
                return app_obj["DataFields"]

        return None

    def app_name_to_app_obj(self, app_name):
        for app_obj in self._app_objects:
            if app_name == app_obj["ApplicationName"]:
                return app_obj

        return None
