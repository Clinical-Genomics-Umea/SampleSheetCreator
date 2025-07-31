from logging import Logger
import json

import jsonschema
from jsonschema import validate

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.indexes.index_kit import IndexKit


class IndexKitManager(object):
    def __init__(self, configuration_manager: ConfigurationManager, logger: Logger):
        self._logger = logger
        self._configuration_manager = configuration_manager

        self._index_schemas = self._load_schemas()
        self._index_kit_data = self._load_index_data()

        self._index_kit_objects = self._get_index_kit_objects(self._index_kit_data)

    @staticmethod
    def _get_index_kit_objects(index_kit_data):
        if isinstance(index_kit_data, dict):
            # If it's a dictionary, convert it to a list of its values
            return [IndexKit(ikd) for ikd in index_kit_data.values()]
        elif isinstance(index_kit_data, list):
            # If it's already a list, process it directly
            return [IndexKit(ikd) for ikd in index_kit_data]
        else:
            raise ValueError(f"Unexpected type for index_kit_data: {type(index_kit_data)}. Expected dict or list.")

    def _load_schemas(self) -> dict:
        """Load and validate JSON schemas from the configuration directory.
        
        Returns:
            dict: A dictionary mapping schema names to their loaded JSON content.
            
        Raises:
            Exception: If there's an unexpected error loading the schemas.
        """
        root_path = self._configuration_manager.index_schema_root
        schemas = {}
        
        try:
            for schema_path in root_path.glob("*.json"):
                try:
                    with open(schema_path, "r", encoding='utf-8') as schema_fh:
                        schema_name = schema_path.stem  # Get filename without extension
                        schemas[schema_name] = json.load(schema_fh)
                        self._logger.debug(f"Successfully loaded schema: {schema_name}")
                except json.JSONDecodeError as e:
                    self._logger.error(f"Invalid JSON in schema file {schema_path}: {e}")
                    continue
                except OSError as e:
                    self._logger.error(f"Error reading schema file {schema_path}: {e}")
                    continue
                    
        except Exception as e:
            self._logger.critical(f"Unexpected error loading schemas: {e}")
            raise
            
        if not schemas:
            self._logger.warning("No schema files found in %s", root_path)
            
        return schemas

    def _load_index_data(self) -> list[dict]:
        """Load and validate index kit data from JSON files.
        
        Returns:
            list[dict]: A list of validated index kit data dictionaries.
            
        Raises:
            FileNotFoundError: If the index kits directory doesn't exist.
            jsonschema.ValidationError: If any index kit data fails validation.
        """
        index_kit_root = self._configuration_manager.index_kits_root
        
        if not index_kit_root.exists():
            self._logger.error(f"Index kits directory not found: {index_kit_root}")
            raise FileNotFoundError(f"Index kits directory not found: {index_kit_root}")
            
        index_data = []
        
        for index_json in index_kit_root.glob("*.json"):
            try:
                with open(index_json, "r", encoding='utf-8') as index_json_fh:
                    try:
                        indata = json.load(index_json_fh)
                    except json.JSONDecodeError as e:
                        self._logger.error(f"Invalid JSON in file {index_json}: {e}")
                        continue
                        
                    kit_type = indata.get('Type')
                    layout = indata.get('Layout')

                    if not all([kit_type, layout]):
                        self._logger.error(f"Missing required fields (Type/Layout) in {index_json}")
                        continue

                    schema_name = f"{kit_type}_{layout}"

                    if schema_name not in self._index_schemas:
                        self._logger.error(f"Schema not found for {index_json}: {schema_name}")
                        continue

                    try:
                        validate(instance=indata, schema=self._index_schemas[schema_name])
                        index_data.append(indata)
                        self._logger.debug(f"Successfully loaded and validated {index_json}")
                    except jsonschema.ValidationError as e:
                        self._logger.error(f"Validation failed for {index_json}: {e}")
                        continue
                        
            except OSError as e:
                self._logger.error(f"Error reading file {index_json}: {e}")
                continue

        if not index_data:
            self._logger.warning(f"No valid index kit data found in {index_kit_root}")
            
        return index_data

    @property
    def index_kit_objects(self):
        return self._index_kit_objects
