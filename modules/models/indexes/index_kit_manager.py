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

        schema_root = self._configuration_manager.index_schema_root
        data_root = self._configuration_manager.index_data_root

        self._index_schemas = self._load_index_validation_schemas(schema_root)
        self._index_data = self._load_index_data(data_root)

        self._index_kits = self._get_index_kits(self._index_data)

    def _load_index_validation_schemas(self, root_path):
        index_schema_paths = [ik for ik in root_path.glob("*.json")]
        schemas = []

        for schema_path in index_schema_paths:
            with open(schema_path, "r") as schema_fh:

                schema = json.load(schema_fh)

                if schema['$schema'] != "http://json-schema.org/draft-04/schema#":
                    self._logger.error(f"schema {schema_path} is not a draft 4 schema")
                    continue

                if not "IndexStrategy" in schema.get("properties", {}):
                    self._logger.error(f"schema {schema_path} has not an index_strategy property")
                    continue

                if not "Layout" in schema.get("properties", {}):
                    self._logger.error(f"schema {schema_path} has not a layout property")
                    continue

                schemas.append(schema)

        return schemas


    def _get_schema(self, strategy, layout):
        for schema in self._index_schemas:
            if not "IndexStrategy" in schema.get("properties", {}):
                continue

            if not "Layout" in schema.get("properties", {}):
                continue

            if (schema['properties']['IndexStrategy']['const'] == strategy and
                schema['properties']['Layout']['const'] == layout):
                return schema
                
        self._logger.warning(f"No schema found for index_strategy: {strategy}, layout: {layout}")
        return None


    @staticmethod
    def _get_index_kits(index_kit_data):

        return [IndexKit(ik) for ik in index_kit_data]

    def _load_index_data(self, index_data_root):

        index_data_paths = [index_data_path for index_data_path in index_data_root.glob("*.json")]

        index_data_list = []
        for index_path in index_data_paths:
            with open(index_path, "r") as index_json_fh:
                index_data = json.load(index_json_fh)

                strategy = index_data.get('IndexStrategy')
                layout = index_data.get('Layout')

                schema = self._get_schema(strategy, layout)

                if not schema:
                    self._logger.error(f"{index_path} does not have a schema")
                    return None

                try:
                    validate(instance=index_data, schema=schema)
                    index_data_list.append(index_data)

                except jsonschema.ValidationError as e:
                    self._logger.error(f"validation of {index_path} failed")

        return index_data_list

    @property
    def index_kits(self):
        return self._index_kits
