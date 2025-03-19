from logging import Logger

from PySide6.QtCore import QObject

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.sample.samplesheet_fns import to_json


class MethodManager(QObject):
    def __init__(self, configuration_manager: ConfigurationManager, application_manager: ApplicationManager, logger: Logger):
        super().__init__()

        self._configuration_manager = configuration_manager
        self._application_manager = application_manager
        self._logger = logger

        self._methods = {}

        self._method_objects = self._configuration_manager.method_configs

        self._setup()

    def _setup(self):

        for method_object in self._method_objects:
            method = method_object.get("Method")

            for method_app_profile_obj in method_object['ApplicationProfiles']:
                method_app_profile = method_app_profile_obj['ApplicationProfile']
                method_app_profile_version = method_app_profile_obj['ApplicationProfileVersion']

                app_profile_obj = self._application_manager.app_profile_to_app_prof_obj(method_app_profile)

                app_profile = app_profile_obj.get("ApplicationProfile")
                app_profile_version = app_profile_obj.get("ApplicationProfileVersion")

                if method_app_profile != app_profile:
                    continue

                if method_app_profile_version == app_profile_version:
                   self._methods[method] = method_object
                else:
                    self._logger.warning(f"in method {method}, application profile {app_profile} version does not match")


    def application_profiles_by_method(self, method):
        return self._methods[method]['ApplicationProfiles']

    def application_profiles_json(self, method):
        profiles = [profile_obj.get("ApplicationProfile")
                    for profile_obj in self._methods[method]['ApplicationProfiles']]
        return to_json(profiles)

    def application_profiles_list(self, method):
        profiles = [profile_obj.get("ApplicationProfile")
                    for profile_obj in self._methods[method]['ApplicationProfiles']]
        return profiles

