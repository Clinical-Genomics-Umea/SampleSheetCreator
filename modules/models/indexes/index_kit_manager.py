from logging import Logger
import json

import jsonschema
from jsonschema import validate

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.indexes.index_kit_object import IndexKitObject


class IndexKitManager(object):
    def __init__(self, configuration_manager: ConfigurationManager, logger: Logger):
        self._logger = logger
        self._configuration_manager = configuration_manager

        self._index_schemas = self._load_schemas()
        self._index_kit_data = self._load_index_data()

        self._index_kit_objects = self._get_index_kit_objects(self._index_kit_data)

    @staticmethod
    def _get_index_kit_objects(index_kit_data):
        return [IndexKitObject(ik) for ik in index_kit_data]

    def _load_schemas(self):

        root_path = self._configuration_manager.index_schema_root
        index_schema_paths = [ik for ik in root_path.glob("*.json")]
        schemas = {}

        for schema_path in index_schema_paths:
            with open(schema_path, "r") as schema_fh:
                name = schema_path.name.split('.')[0]
                schemas[name] = json.load(schema_fh)

        return schemas

    def _load_index_data(self):

        index_kit_root = self._configuration_manager.index_kits_root

        index_jsons = [ik for ik in index_kit_root.glob("*.json")]
        index_data = []
        for index_json in index_jsons:
            with open(index_json, "r") as index_json_fh:
                indata = json.load(index_json_fh)

                kit_type = indata.get('Type')
                layout = indata.get('Layout')

                schema_name = f"{kit_type}_{layout}"

                if schema_name in self._index_schemas:
                    try:
                        validate(instance=indata, schema=self._index_schemas[schema_name])
                    except jsonschema.ValidationError as e:
                        self._logger.error(f"validation of {index_json} failed")
                        return

                    index_data.append(indata)
                else:
                    self._logger.error(f"{index_json} does not have a schema")

        return index_data

    @property
    def index_kit_objects(self):
        return self._index_kit_objects
