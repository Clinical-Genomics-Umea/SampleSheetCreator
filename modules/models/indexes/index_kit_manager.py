"""
Index Kit Manager

This module provides functionality to manage and validate index kits used in sequencing runs.
It handles loading, validating, and querying index kit data from JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import jsonschema
from PySide6.QtCore import QObject, Signal
from jsonschema import validate, ValidationError

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.indexes.index_kit_model import IndexKitModel
from modules.models.state.state_model import StateModel
from modules.views.drawer_tools.index.index_kit_widget import IndexKitWidget


class IndexKitManager(QObject):
    """Manages index kits including loading, validation, and querying.
    
    This class handles the loading of index kit data from JSON files, validates them against
    their respective schemas, and provides methods to query and filter the loaded index kits.
    """

    index_kits_changed = Signal()

    def __init__(self, configuration_manager: ConfigurationManager, state_model: StateModel, logger: Optional[logging.Logger] = None):
        """Initialize the IndexKitManager.
        
        Args:
            configuration_manager: The configuration manager instance
            state_model: The application state model
            logger: Optional logger instance
        """
        super().__init__()
        
        self._configuration_manager = configuration_manager
        self._state_model = state_model
        self._logger = logger or logging.getLogger(__name__)

        # Initialize other instance variables
        self._index_kit_data = {}
        self._schemas = {}
        self._index_kit_widgets = []
        
        # Load data
        self._load()

    def on_run_cycles_changed(self) -> None:
        self._index_kit_widgets = self._set_index_kit_widgets_by_run_cycles()
        print("on_run_cycles_changed")
        self.index_kits_changed.emit()

    
    def _load(self) -> None:
        """Reload all index kit data and schemas."""
        self._index_schemas = self._load_schemas()
        self._index_kit_data = self._load_index_data()

    def _set_index_kit_widgets_by_run_cycles(self) -> List[IndexKitWidget]:
        _, run_cycles_index_i7_len, run_cycles_index_i5_len, _ = self._state_model.run_cycles

        index_kit_widgets = []

        for index_kit_dataset in self._index_kit_data:
            # First create the IndexKitModel from the dataset
            try:
                index_kit_model = IndexKitModel(index_kit_dataset)
                # Then create the widget with the model's data
                if (index_kit_model.index_i7_len <= run_cycles_index_i7_len and 
                    index_kit_model.index_i5_len <= run_cycles_index_i5_len):
                    index_kit_widgets.append(IndexKitWidget(index_kit_dataset))
            except Exception as e:
                self._logger.error(f"Error creating index kit widget: {e}")
                continue

        return index_kit_widgets

    @property
    def index_kit_widgets(self) -> List[IndexKitWidget]:
        return self._index_kit_widgets

    
    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load and validate JSON schemas from the configuration directory.
        
        Returns:
            Dictionary mapping schema names to their loaded JSON content.
            
        Raises:
            OSError: If there's an error reading the schema files.
            json.JSONDecodeError: If a schema file contains invalid JSON.
        """
        root_path = self._configuration_manager.index_schema_root
        schemas: Dict[str, Dict[str, Any]] = {}
        
        if not root_path.exists():
            self._logger.warning("Schema directory does not exist: %s", root_path)
            return {}
            
        for schema_path in root_path.glob("*.json"):
            try:
                with open(schema_path, "r", encoding='utf-8') as schema_fh:
                    schema_name = schema_path.stem
                    schemas[schema_name] = json.load(schema_fh)
                    self._logger.debug("Successfully loaded schema: %s", schema_name)
            except json.JSONDecodeError as e:
                self._logger.error("Invalid JSON in schema file %s: %s", schema_path, e)
                continue
            except OSError as e:
                self._logger.error("Error reading schema file %s: %s", schema_path, e)
                continue
                
        if not schemas:
            self._logger.warning("No valid schema files found in %s", root_path)
            
        return schemas
    
    def _load_index_data(self) -> List[Dict[str, Any]]:
        """Load and validate index kit data from JSON files.
        
        Returns:
            List of validated index kit data dictionaries.
            
        Raises:
            FileNotFoundError: If the index kits directory doesn't exist.
        """
        index_kit_root = self._configuration_manager.index_kits_root
        index_data: List[Dict[str, Any]] = []
        
        if not index_kit_root.exists():
            self._logger.error("Index kits directory not found: %s", index_kit_root)
            raise FileNotFoundError(f"Index kits directory not found: {index_kit_root}")
            
        for index_json in index_kit_root.glob("*.json"):
            try:
                with open(index_json, "r", encoding='utf-8') as index_json_fh:
                    try:
                        indata = json.load(index_json_fh)
                    except json.JSONDecodeError as e:
                        self._logger.error("Invalid JSON in file %s: %s", index_json, e)
                        continue
                        
                    if not self._validate_index_data(indata, index_json):
                        continue
                        
                    index_data.append(indata)
                    self._logger.debug("Successfully loaded and validated %s", index_json)
                        
            except OSError as e:
                self._logger.error("Error reading file %s: %s", index_json, e)
                continue

        if not index_data:
            self._logger.warning("No valid index kit data found in %s", index_kit_root)
            
        return index_data
    
    def _validate_index_data(self, data: Dict[str, Any], file_path: Path) -> bool:
        """Validate index kit data against its schema.
        
        Args:
            data: The index kit data to validate.
            file_path: Path to the file being validated (for error messages).
            
        Returns:
            bool: True if validation succeeds, False otherwise.
        """
        kit_type = data.get('Type')
        layout = data.get('Layout')

        if not all([kit_type, layout]):
            self._logger.error(
                "Missing required fields (Type/Layout) in %s: Type=%s, Layout=%s",
                file_path, kit_type, layout
            )
            return False

        schema_name = f"{kit_type}_{layout}"

        if schema_name not in self._index_schemas:
            self._logger.error("Schema not found for %s: %s", file_path, schema_name)
            return False

        try:
            validate(instance=data, schema=self._index_schemas[schema_name])
            return True
        except ValidationError as e:
            self._logger.error("Validation failed for %s: %s", file_path, e)
            return False
    
    def get_kit_by_name(self, name: str) -> Optional[IndexKitModel]:
        """Get an index kit by its name.
        
        Args:
            name: The name of the index kit to find.
            
        Returns:
            The matching IndexKit or None if not found.
        """
        for kit in self._index_kit_widgets:
            if kit.name == name:
                return kit
        return None
    
    def get_kits_by_type(self, kit_type: str) -> List[IndexKitModel]:
        """Get all index kits of a specific type.
        
        Args:
            kit_type: The type of index kits to find.
            
        Returns:
            List of matching IndexKit objects.
        """
        return [kit for kit in self._index_kit_widgets if kit.type == kit_type]
    
    def get_kits_by_layout(self, layout: str) -> List[IndexKitModel]:
        """Get all index kits with a specific layout.
        
        Args:
            layout: The layout of index kits to find.
            
        Returns:
            List of matching IndexKit objects.
        """
        return [kit for kit in self._index_kit_widgets if kit._layout == layout]
    
    def get_all_kit_types(self) -> List[str]:
        """Get a list of all unique kit types.
        
        Returns:
            List of unique kit type names.
        """
        return list({kit.type for kit in self._index_kit_widgets})
    
    def get_all_layouts(self) -> List[str]:
        """Get a list of all unique layouts.
        
        Returns:
            List of unique layout names.
        """
        return list({kit._layout for kit in self._index_kit_widgets})
    
    @property
    def index_kit_objects(self) -> List[IndexKitModel]:
        """Get all loaded index kit objects.
        
        Returns:
            List of all IndexKit objects.
        """
        return self._index_kit_widgets
    
    @property
    def index_kit_data(self) -> List[Dict[str, Any]]:
        """Get the raw index kit data.
        
        Returns:
            List of raw index kit data dictionaries.
        """
        return self._index_kit_data
    
    @property
    def index_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get the loaded schema definitions.
        
        Returns:
            Dictionary mapping schema names to their definitions.
        """
        return self._index_schemas
