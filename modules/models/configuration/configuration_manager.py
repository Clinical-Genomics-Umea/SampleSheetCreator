import re
from typing import Optional
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, Tuple
import yaml
from PySide6.QtCore import QSettings, QObject, Signal, Slot
import getpass
import keyring

# Custom Exceptions
class ConfigError(Exception):
    """Base exception for configuration related errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.details = details or {}
        super().__init__(message)

class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        self.field_errors = field_errors or {}
        super().__init__(f"Configuration validation failed: {message}")

class ConfigLoadError(ConfigError):
    """Raised when there is an error loading a configuration file."""
    def __init__(self, path: Path, message: str):
        super().__init__(f"Failed to load config from {path}: {message}")
        self.path = path

class ConfigurationManager(QObject):
    """Centralized configuration manager for the application.
    
    This class handles loading, validating, and providing access to various
    configuration files and settings used throughout the application. It also
    manages user-related settings and provides signals for notifying about
    configuration changes.
    
    Signals:
        run_data_changed: Emitted when run data is updated. Passes the new run data as a dict.
        users_changed: Emitted when the user list is modified.
        run_data_error: Emitted when there's an error with run data. Passes a list of error fields.
    """
    
    # Signals
    run_data_changed = Signal(dict)  # Emitted when run data is updated
    users_changed = Signal()         # Emitted when user list changes
    run_data_error = Signal(list)    # Emitted with list of invalid fields on validation error
    
    # Default configuration paths (relative to application root)
    # Regular expression for validating read cycles format (e.g., "151-8-8-151")
    _READ_CYCLES_PATTERN = re.compile(r'^\d+(-\d+)*$')
    
    # Application settings organization and name for QSettings
    _QT_ORGANIZATION = "Region Västerbotten"
    _QT_APPLICATION = "samplecheater"

    # Default folder paths keys
    _DEFAULT_FOLDER_PATHS = {
        'export_samplesheet_path': 'default_paths/export_samplesheet',
        'export_json_path': 'default_paths/export_json',
        'export_package_path': 'default_paths/export_package'
    }

    # Default configuration paths (relative to application root)
    _DEFAULT_CONFIG_PATHS = {
        'index_config_root_path': 'config/indexes/data',
        'index_schema_root_path': 'json_schemas/index',
        'application_profiles_root_path': 'config/applications/application_profiles',
        'test_profiles_root_path': 'config/tests/test_profiles',
        'run_settings_file_path': 'config/run/run_settings.yaml',
        'instrument_data_config_file_path': 'config/run/instrument_data.yaml',
        'sample_settings_file_path': 'config/sample_settings.yaml',
        'validation_settings_file_path': 'config/validation/validation_settings.yaml',
        'samplesheet_v1_template_file_path': 'config/samplesheet_v1.yaml',
    }

    def __init__(self, logger: Logger, config_paths: Optional[Dict[str, str]] = None):
        """Initialize the configuration manager.
        
        Args:
            logger: Logger instance to use for logging.
            config_paths: Optional dictionary of custom configuration paths to override defaults.
                         Keys should match those in DEFAULT_CONFIG_PATHS.
                         
        Raises:
            ConfigError: If there's an error loading or validating the configuration.
        """
        super().__init__()

        # Use provided logger (required)
        if logger is None:
            raise ValueError("Logger must be provided to ConfigurationManager")

        self._logger = logger
        self._qt_settings = QSettings(self._QT_ORGANIZATION, self._QT_APPLICATION)
        self._run_data_is_set = False
        
        self._logger.info("Initializing ConfigurationManager")
        
        # Initialize paths
        self._paths = self._init_paths(config_paths or {})

        # Load all configurations
        self._load_configurations()

        # Load application and method configs in parallel if possible
        self._application_configs = self._load_configs_from_dir(
            self._paths['application_profiles_root_path']
        )
        self._test_configs = self._load_configs_from_dir(
            self._paths['test_profiles_root_path']
        )

        self._logger.info("ConfigurationManager initialized successfully")

    @staticmethod
    def set_igene_key(api_key: str):
        service_name = "igene"
        user_name = getpass.getuser()
        keyring.set_password(service_name, user_name, api_key)

    @property
    def igene_key(self):
        service_name = "igene"
        user_name = getpass.getuser()
        return keyring.get_password(service_name, user_name)

    def _init_paths(self, custom_paths: Dict[str, str]) -> Dict[str, Path]:
        """Initialize and validate all configuration paths.
        
        Args:
            custom_paths: Dictionary of custom paths to override defaults.
                          Keys should match those in _DEFAULT_PATHS.
            
        Returns:
            Dictionary mapping configuration names to absolute Path objects.
            
        Raises:
            ConfigError: If any required configuration directory cannot be created.
        """
        self._logger.debug("Initializing configuration paths")
        paths: Dict[str, Path] = {}

        for key, default_path in self._DEFAULT_CONFIG_PATHS.items():
            # Get path from custom paths or use default
            path_str = str(custom_paths.get(key, default_path))
            path = Path(path_str).resolve()
            paths[key] = path

        self._logger.debug("All configuration paths initialized successfully")
        return paths

    def _load_configurations(self) -> None:
        """Load and validate all configuration files.
        
        This method loads the following configuration files:
        - Run settings (including widget configurations)
        - Instrument data
        - Sample settings
        - Validation settings
        - Sample sheet template
        
        Raises:
            ConfigError: If any required configuration file is missing or invalid.
        """
        self._logger.info("Loading configuration files")
        
        # Load run settings first as it contains configurations needed by other components
        self._run_settings = self._load_config_file(
            self._paths['run_settings_file_path'],
            "run settings",
            required_keys=["RunViewFields", "RunSetupWidgets", "RunDataFields", "ReadCyclesFields"]
        )
        
        # Extract configuration sections
        self._run_view_widgets_config = self._run_settings["RunViewFields"]
        self._run_setup_widgets_config = self._run_settings["RunSetupWidgets"]
        self._run_data_fields = self._run_settings["RunDataFields"]
        self._read_cycles_fields = self._run_settings["ReadCyclesFields"]
        
        # Load other configurations
        self._instrument_data = self._load_config_file(
            self._paths['instrument_data_config_file_path'],
            "instrument data"
        )
        
        self._samples_settings = self._load_config_file(
            self._paths['sample_settings_file_path'],
            "sample settings",
            required_keys=["required_fields"]
        )
        self._required_sample_fields = self._samples_settings["required_fields"]
        
        self._validation_settings = self._load_config_file(
            self._paths['validation_settings_file_path'],
            "validation settings"
        )
        
        self._samplesheet_v1_template = self._load_config_file(
            self._paths['samplesheet_v1_template_file_path'],
            "sample sheet template"
        )
        
        self._logger.info("All configuration files loaded successfully")
            
    def _load_config_file(self, path: Path, config_name: str, 
                         required_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Load and validate a configuration file.
        
        Args:
            path: Path to the configuration file.
            config_name: Human-readable name of the configuration (for error messages).
            required_keys: List of top-level keys that must be present in the config.
            
        Returns:
            Parsed configuration as a dictionary.
            
        Raises:
            ConfigError: If the file cannot be loaded, parsed, or is missing required keys.
        """
        self._logger.debug("Loading %s from %s", config_name, path)
        
        try:
            # Load the YAML file
            config = self._load_yaml(path)
            
            # Validate required keys if specified
            if required_keys:
                missing_keys = [key for key in required_keys if key not in config]
                if missing_keys:
                    raise ConfigError(
                        f"Missing required keys in {config_name}: {', '.join(missing_keys)}",
                        {"missing_keys": missing_keys, "path": str(path)}
                    )
            
            self._logger.debug("Successfully loaded %s", config_name)
            return config
            
        except ConfigError:
            raise  # Re-raise ConfigError with context
        except Exception as e:
            raise ConfigError(
                f"Failed to load {config_name} from {path}: {str(e)}",
                {"path": str(path), "error": str(e)}
            ) from e
            
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Safely load and parse a YAML file.
        
        Args:
            path: Path to the YAML file.
            
        Returns:
            Parsed YAML content as a dictionary.
            
        Raises:
            ConfigError: If the file cannot be read or parsed as YAML.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(
                f"Invalid YAML in {path}",
                {"path": str(path), "error": str(e)}
            ) from e
        except OSError as e:
            raise ConfigError(
                f"Could not read file {path}",
                {"path": str(path), "error": str(e)}
            ) from e
            
    def _load_configs_from_dir(self, config_dir: Path) -> List[Dict[str, Any]]:
        """Load and validate all YAML configs from a directory.
        
        Args:
            config_dir: Directory containing YAML config files.
            
        Returns:
            List of successfully loaded configuration dictionaries.
            
        Note:
            Files that fail to load are logged as errors but don't stop processing
            of other files in the directory.
        """
        self._logger.debug("Loading configurations from directory: %s", config_dir)
        
        if not config_dir.exists():
            self._logger.warning("Configuration directory not found: %s", config_dir)
            return []
            
        if not config_dir.is_dir():
            self._logger.error("Configuration path is not a directory: %s", config_dir)
            return []
            
        configs = []
        yaml_files = list(config_dir.glob('**/*.yaml')) + list(config_dir.glob('**/*.yml'))
        
        if not yaml_files:
            self._logger.warning("No YAML files found in directory: %s", config_dir)
            return []
            
        for config_file in yaml_files:
            try:
                config = self._load_yaml(config_file)
                configs.append(config)
                self._logger.debug("Loaded configuration from %s", config_file.name)
            except ConfigError as e:
                self._logger.error("Skipping invalid config file %s: %s", 
                                 config_file.name, str(e))
                continue
                
        self._logger.info("Loaded %d/%d configurations from %s", 
                         len(configs), len(yaml_files), config_dir)
        return configs

    @property
    def instrument_data(self) -> Dict[str, Any]:
        """Get instrument configuration data.
        
        Returns:
            Dictionary containing instrument configuration
        """
        return self._instrument_data
        
    @property
    def test_profiles_dict_list(self) -> List[Dict[str, Any]]:
        """Get all method configurations.
        
        Returns:
            List of method configuration dictionaries
        """
        return self._test_configs
        
    @property
    def application_configs(self) -> List[Dict[str, Any]]:
        """Get all application configurations.
        
        Returns:
            List of application configuration dictionaries
        """
        return self._application_configs

    @property
    def index_kits_root(self) -> Path:
        """Get the root directory for index kit configurations.
        
        Returns:
            Path to the index kits directory
        """
        return self._paths['index_config_root_path']

    @property
    def index_schema_root_path(self) -> Path:
        """Get the root directory for index schema files.
        
        Returns:
            Path to the index schema directory
        """
        return self._paths['index_schema_root_path']

    @property
    def instrument_flowcells(self) -> Dict[str, Any]:
        """Get instrument and flowcell configurations.
        
        Returns:
            Dictionary containing instrument and flowcell configurations
        """
        return self._instrument_data

    @property
    def run_data_fields(self) -> List[str]:
        """Get the list of run data fields.
        
        Returns:
            List of field names for run data
        """
        return self._run_data_fields

    @property
    def read_cycles_fields(self) -> List[str]:
        """Get the list of read cycles fields.
        
        Returns:
            List of read cycle field names
        """
        return self._read_cycles_fields

    @property
    def samplesheet_v1_template(self) -> Dict[str, Any]:
        """Get the v1 sample sheet template.
        
        Returns:
            Dictionary containing the sample sheet template
        """
        return self._samplesheet_v1_template

    @property
    def required_sample_fields(self) -> List[str]:
        """Get the list of required sample fields.
        
        Returns:
            List of required field names for samples
        """
        return self._samples_settings.get("required_fields", [])

    @property
    def run_lanes(self) -> List[int]:
        """Get the list of available run lanes.
        
        Returns:
            List of lane numbers
        """
        return self._run_settings.get("Lanes", [])

    @property
    # def samplesheet_header_data(self) -> Dict[str, str]:
    #     """Generate header data for the sample sheet.
    #
    #     Returns:
    #         Dictionary containing header fields for the sample sheet
    #     """
    #     return {
    #         "FileFormatVersion": self._run_data.sample_sheet_version,
    #         "InstrumentType": self._run_data.instrument,
    #         "RunName": self._run_data.run_name,
    #         "RunDescription": self._run_data.run_description,
    #         "Custom_Flowcell": self._run_data.flowcell,
    #         "Custom_UUID7": self._run_data.uuid,
    #     }
    #
    # @property
    # def samplesheet_read_cycles(self) -> Dict[str, str]:
    #     """Get read cycle information for the sample sheet.
    #
    #     Returns:
    #         Dictionary mapping read cycle types to their values
    #
    #     Raises:
    #         ConfigError: If the read cycles format is invalid
    #     """
    #     if not self._run_data.read_cycles:
    #         return {}
    #
    #     read_cycle_headers = [
    #         "Read1Cycles",
    #         "Index1Cycles",
    #         "Index2Cycles",
    #         "Read2Cycles",
    #     ]
    #
    #     read_cycles = self._run_data.read_cycles.strip()
    #     cycle_parts = read_cycles.split("-")
    #
    #     if len(cycle_parts) != len(read_cycle_headers):
    #         raise ConfigError(f"Invalid read cycles format: {read_cycles}")
    #
    #     return dict(zip(read_cycle_headers, cycle_parts))

    @property
    def i5_samplesheet_orientation(self) -> str:
        """Get the i5 sample sheet orientation setting.
        
        Returns:
            The orientation string (e.g., '5prime' or '3prime')
        """
        return self._run_data.i5_samplesheet_orientation

    @property
    def base_colors(self) -> Dict[str, str]:
        """Get the base color configuration.
        
        Returns:
            Dictionary mapping base names to their color codes
        """
        return {
            "A": self._run_data.color_a,
            "T": self._run_data.color_t,
            "G": self._run_data.color_g,
            "C": self._run_data.color_c,
        }

    @property
    def instruments(self) -> List[str]:
        """Get the list of available instruments.
        
        Returns:
            List of instrument names
        """
        return list(self._instrument_data.keys())

    @property
    def run_setup_widgets_config(self) -> Dict[str, Any]:
        """Get the run setup widgets configuration.
        
        Returns:
            Dictionary containing widget configurations for run setup
        """
        return self._run_setup_widgets_config

    @property
    def run_view_widgets_config(self) -> Dict[str, Any]:
        """Get the run view widgets configuration.
        
        Returns:
            Dictionary containing widget configurations for run view
        """
        return self._run_view_widgets_config

    # @property
    # def run_data(self) -> RunData:
    #     """Get the current run data.
    #
    #     Returns:
    #         RunData object containing the current run configuration
    #     """
    #     return self._run_data

    def validate_run_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate run data before updating the configuration.
        
        Args:
            data: Dictionary containing run data to validate
            
        Returns:
            Tuple of (is_valid, error_fields) where:
            - is_valid: True if data is valid, False otherwise
            - error_fields: List of field names with validation errors
        """
        error_fields = []

        # Validate custom read cycles if provided
        custom_read_cycles = data.get("CustomReadCycles", "").strip()
        if custom_read_cycles:
            read_cycles = data.get("ReadCycles", "").strip()
            
            if not read_cycles:
                error_fields.append("ReadCycles")
            else:
                try:
                    rc_parts = [int(x) for x in read_cycles.split("-")]
                    crc_parts = [int(x) for x in custom_read_cycles.split("-")]
                    
                    if len(rc_parts) != len(crc_parts):
                        error_fields.append("CustomReadCycles")
                    else:
                        for rc, crc in zip(rc_parts, crc_parts):
                            if rc < crc:
                                error_fields.append("CustomReadCycles")
                                break
                except (ValueError, AttributeError):
                    error_fields.extend(["ReadCycles", "CustomReadCycles"])

        # Validate required fields
        if not data.get("RunName", "").strip():
            error_fields.append("RunName")
            
        if not data.get("RunDescription", "").strip():
            error_fields.append("RunDescription")
            
        # Validate instrument and flowcell
        instrument = data.get("Instrument")
        flowcell = data.get("Flowcell")
        
        if not instrument or instrument not in self._instrument_data:
            error_fields.append("Instrument")
        elif flowcell and flowcell not in self._instrument_data[instrument].get("Flowcell", {}):
            error_fields.append("Flowcell")

        if error_fields:
            self.run_data_error.emit(error_fields)
            return False, error_fields
            
        return True, []

    # def _update_run_data(self, run_data: Dict[str, Any]) -> None:
    #     """Update run data with values from the provided dictionary.
    #
    #     Args:
    #         run_data: Dictionary containing run data to update
    #     """
    #     for key, value in run_data.items():
    #         if hasattr(self._run_data, key):
    #             setattr(self._run_data, key, value)
    #
    # @Slot(dict)
    # def set_run_data(self, run_data: Dict[str, Any]) -> None:
    #     """Set the run data configuration and validate it.
    #
    #     If the data is invalid, emits the run_data_error signal with a list of invalid fields.
    #     Otherwise, updates the configuration and emits the run_data_changed signal.
    #
    #     Args:
    #         run_data: Dictionary containing the run data to set
    #     """
    #     # Validate the run data
    #     is_valid, error_fields = self.validate_run_data(run_data)
    #     if not is_valid:
    #         self.run_data_error.emit(error_fields)
    #         return
    #
    #     try:
    #         # Update the run data with the new values
    #         self._update_run_data(run_data)
    #
    #         # Apply instrument-specific settings
    #         instrument = run_data["Instrument"]
    #         flowcell = run_data.get("Flowcell")
    #
    #         if instrument in self._instrument_data:
    #             instrument_settings = self._instrument_data[instrument]
    #
    #             # Apply base instrument settings
    #             for key, value in instrument_settings.items():
    #                 if not isinstance(value, dict) and hasattr(self._run_data, key.lower()):
    #                     setattr(self._run_data, key.lower(), value)
    #
    #             # Apply flowcell-specific settings if available
    #             if flowcell and "Flowcell" in instrument_settings:
    #                 flowcell_settings = instrument_settings["Flowcell"].get(flowcell, {})
    #                 for key, value in flowcell_settings.items():
    #                     if hasattr(self._run_data, key.lower()):
    #                         setattr(self._run_data, key.lower(), value)
    #
    #             # Apply color settings from fluorophores
    #             if "Fluorophores" in instrument_settings:
    #                 for base, color in instrument_settings["Fluorophores"].items():
    #                     attr_name = f"color_{base.lower()}"
    #                     if hasattr(self._run_data, attr_name):
    #                         setattr(self._run_data, attr_name, color)
    #
    #         # Update timestamps and UUID
    #         self._run_data.date = datetime.now().strftime("%Y-%m-%d")
    #         self._run_data.uuid = uuid()
    #
    #         # Mark as set and emit change signal
    #         self._run_data_is_set = True
    #         self.run_data_changed.emit(self._run_data.__dict__)
    #
    #     except Exception as e:
    #         self._logger.error(f"Failed to update run data: {e}")
    #         self.run_data_error.emit(["_system"])
    #         raise ConfigError(f"Failed to update run data: {e}")
    #
    # @property
    # def run_data_is_set(self) -> bool:
    #     """Check if run data has been set.
    #
    #     Returns:
    #         True if run data has been set, False otherwise
    #     """
    #     return self._run_data_is_set
    #
    # @property
    # def run_data_changed(self) -> Signal:
    #     """Signal emitted when run data is changed.
    #
    #     Returns:
    #         Qt signal with the updated run data
    #     """
    #     return self._run_data_changed
    #
    # @property
    # def run_data_error(self) -> Signal:
    #     """Signal emitted when there's an error with run data.
    #
    #     Returns:
    #         Qt signal with a list of error fields
    #     """
    #     return self._run_data_error

    @property
    def user_list(self) -> list[str]:
        """Get all user lists from QSettings.
        
        Returns:
            Dictionary mapping user IDs to user information
        """
        return self._qt_settings.value("user_list", []) or []

    @Slot(str, str, str)
    def add_user(self, user_name: str) -> bool:
        """Add a new user to the configuration.
        
        Args:
            user_name: Full name of the user

        Returns:
            True if user was added, False if user already exists
            
        Raises:
            ValueError: If any of the parameters are empty or invalid
        """
        if not user_name:
            raise ValueError("User name is required")
            
        user_list = self.user_list

        if user_name in user_list:
            self._logger.warning(f"User with ID {user_name} already exists")
            return False

        user_list.append(user_name)

        self._qt_settings.setValue("user_list", user_list)
        self.users_changed.emit()
        self._logger.info(f"Added user: {user_name}")
        return True

    @Slot(str)
    def remove_user(self, user_name: str) -> bool:
        """Remove a user from the configuration.
        
        Args:
            user_name: ID of the user to remove
            
        Returns:
            True if user was removed, False if user didn't exist
        """
        if not user_name:
            return False
            
        user_list = self.user_list

        if user_name not in user_list:
            self._logger.warning(f"User {user_name} not found")
            return False

        user_list.remove(user_name)

        self._qt_settings.setValue("user_list", user_list)
        self.users_changed.emit()
        self._logger.info(f"Removed user: {user_name})")
        return True

    @property
    def users(self) -> List[str]:
        """Get a list of all users.
        
        Returns:
            List of users
        """

        return self.user_list

    @property
    def all_config_paths(self) -> Dict[str, Path]:
        """Get absolute paths to all configuration directories.
        
        Returns:
            Dictionary mapping configuration names to their absolute paths
        """
        return {k: v.absolute() for k, v in self._paths.items()}

    @property
    def application_settings_basepath(self) -> Path:
        """Get the base path for application settings.
        
        Returns:
            Path to the application settings directory
        """
        return self._paths.get('application_def', Path())

    @property
    def samples_settings(self) -> Dict[str, Any]:
        """Get the samples settings configuration.
        
        Returns:
            Dictionary containing samples settings
        """
        return self._samples_settings

    def get_folder_path(self, path_type: str) -> str:
        """Get a saved folder path from settings.
        
        Args:
            path_type: One of 'export_samplesheet_path', 'export_json_path', or 'export_package_path'
            
        Returns:
            str: The saved path or empty string if not set
            
        Raises:
            ValueError: If an invalid path_type is provided
        """
        if path_type not in self._DEFAULT_FOLDER_PATHS:
            raise ValueError(f"Invalid path_type: {path_type}. Must be one of {list(self._DEFAULT_FOLDER_PATHS.keys())}")
            
        return self._qt_settings.value(self._DEFAULT_FOLDER_PATHS[path_type], "", type=str)
    
    def set_folder_path(self, path_type: str, path: str) -> bool:
        """Save a folder path to settings.
        
        Args:
            path_type: One of 'export_samplesheet_path', 'export_json_path', or 'export_package_path'
            path: The path to save
            
        Returns:
            bool: True if the path was saved successfully
            
        Raises:
            ValueError: If an invalid path_type is provided
        """
        if path_type not in self._DEFAULT_FOLDER_PATHS:
            raise ValueError(f"Invalid path_type: {path_type}. Must be one of {list(self._DEFAULT_FOLDER_PATHS.keys())}")
            
        self._qt_settings.setValue(self._DEFAULT_FOLDER_PATHS[path_type], path)
        return True
