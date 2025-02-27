from pathlib import Path
import json

import jsonschema
from jsonschema import validate

from modules.models.indexes.index_kit_object import IndexKitObject


class IndexKitManager(object):
    def __init__(self, index_kits_path: Path, schema_path: Path):
        self._index_kits_path = index_kits_path
        self._schema = self._load_schema(schema_path)
        self._index_kit_json_data = self._load_index_data(index_kits_path)
        # print(self._index_kit_json_data)
        self._index_kit_objects = self._get_index_kit_objects(self._index_kit_json_data)

    @staticmethod
    def _get_index_kit_objects(index_kit_data):
        return [IndexKitObject(ik) for ik in index_kit_data]

    @staticmethod
    def _load_schema(schema_path: Path):
        with open(schema_path, "r") as schema_fh:
            return json.load(schema_fh)

    def _load_index_data(self, index_kit_path: Path):
        index_jsons = [ik for ik in index_kit_path.glob("*.json")]
        index_data = []
        for index_json in index_jsons:
            with open(index_json, "r") as index_json_fh:
                indata = json.load(index_json_fh)
                try:
                    validate(instance=indata, schema=self._schema)
                except jsonschema.ValidationError as e:
                    self._index_import_error = e
                    return

                index_data.append(indata)

        return index_data

    @property
    def index_kit_objects(self):
        return self._index_kit_objects
