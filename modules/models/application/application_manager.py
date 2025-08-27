from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from logging import Logger

from modules.models.configuration.configuration_manager import ConfigurationManager


@dataclass
class ApplicationProfile:
    """Represents an application profile configuration."""
    application_profile_name: str
    application_name: str
    application_type: str
    application_profile_version: str
    settings: Dict[str, Any]
    data: Dict[str, Any]
    data_fields: Dict[str, Any]


class ApplicationManager:
    """Manages application profiles and provides lookup functionality."""
    
    def __init__(self, config_manager: ConfigurationManager, logger: Logger) -> None:
        """Initialize the ApplicationManager.
        
        Args:
            config_manager: The configuration manager containing application configs
            logger: Logger instance for logging messages
        """
        self._logger = logger
        self._profiles: List[Dict[str, Any]] = config_manager.application_configs
        
        # Create lookup dictionaries
        self._profile_name_to_application_name: Dict[str, str] = {}
        self._application_name_to_application_type: Dict[str, str] = {}
        self._profile_name_to_settings: Dict[str, Dict[str, Any]] = {}
        self._profile_name_to_data: Dict[str, Dict[str, Any]] = {}
        self._profile_name_to_data_fields: Dict[str, Dict[str, Any]] = {}
        self._profile_name_to_profile: Dict[str, Dict[str, Any]] = {}
        self._hierarchy: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._profile_name_to_translate: Dict[str, str] = {}
        
        self._initialize_lookups()
    
    def _initialize_lookups(self) -> None:
        """Initialize lookup dictionaries for faster access."""
        self._hierarchy = {}
        
        for profile in self._profiles:
            try:
                profile_name = profile.get("ApplicationProfileName")
                application_name = profile.get("ApplicationName")
                application_type = profile.get("ApplicationType")
                application_profile_version = profile.get("ApplicationProfileVersion")
                translate = profile.get("Translate")
                
                # Skip invalid entries
                if not all([profile_name, application_name, application_type, application_profile_version]):
                    self._logger.warning(f"Skipping invalid application object: {profile}")
                    continue
                
                # Populate lookups
                self._profile_name_to_application_name[profile_name] = application_name
                self._application_name_to_application_type[application_name] = application_type
                self._profile_name_to_settings[profile_name] = profile.get("Settings", {})
                self._profile_name_to_data[profile_name] = profile.get("Data", {})
                self._profile_name_to_data_fields[profile_name] = profile.get("DataFields", {})
                self._profile_name_to_profile[profile_name] = profile
                self._profile_name_to_translate[profile_name] = translate

                # Build hierarchy
                if application_type not in self._hierarchy:
                    self._hierarchy[application_type] = {}

                self._hierarchy[application_type][profile_name] = profile
                
            except KeyError as e:
                self._logger.error(f"Error processing application object {profile}: {str(e)}")
    
    def application_profile_to_app(self, app_profile: str) -> Optional[str]:
        """Get the application name for a given application profile.
        
        Args:
            app_profile: The application profile name
            
        Returns:
            The application name if found, None otherwise
        """
        return self._profile_name_to_application_name.get(app_profile)

    def profile_name_to_data_fields(self, profile_name: str) -> Dict[str, Any]:
        return self._profile_name_to_data_fields.get(profile_name, [])

    def lane_explode_by_profile_name(self, profile_name: str) -> bool:
        profile = self._profile_name_to_profile.get(profile_name)
        return profile.get("LaneExplode", False)
    
    def application_name_to_application_type(self, application_name: str) -> Optional[str]:
        """Get the application type for a given application name.
        
        Args:
            application_name: The application name
            
        Returns:
            The application type if found, None otherwise
        """
        return self._application_name_to_application_type.get(application_name)

    def profile_name_to_translate(self, profile_name: str) -> Optional[str]:
        return self._profile_name_to_translate[profile_name]

    @property
    def application_hierarchy(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get the application hierarchy.
        
        Returns:
            A dictionary mapping application types to profiles to their configurations
        """
        return self._hierarchy
    
    def profile_name_to_settings(self, profile_name: str) -> Dict[str, Any]:
        """Get settings for an application profile.
        
        Args:
            profile_name: The application profile name
            
        Returns:
            The settings dictionary for the profile, or empty dict if not found
        """
        return self._profile_name_to_settings.get(profile_name, {})
    
    def profile_name_to_data(self, profile_name: str) -> Dict[str, Any]:
        """Get data for an application profile.
        
        Args:
            profile_name: The application profile name
            
        Returns:
            The data dictionary for the profile, or empty dict if not found
        """
        return self._profile_name_to_data.get(profile_name, {})


    def profile_name_to_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get the full application profile object.
        
        Args:
            profile_name: The application profile name
            
        Returns:
            The full application profile dictionary if found, None otherwise
        """
        return self._profile_name_to_profile.get(profile_name)

    def profile_name_to_application_name(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get the full application profile object.

        Args:
            profile_name: The application profile name

        Returns:
            The full application profile dictionary if found, None otherwise
        """
        profile = self.profile_name_to_profile(profile_name)

        return profile.get("ApplicationName")
