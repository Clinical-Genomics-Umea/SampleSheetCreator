from functools import reduce

import pandas as pd
from pathlib import Path
import json
import jsonschema
from jsonschema import validate


class IndexKitManager(object):
    def __init__(self, index_kits_path: Path, schema_path: Path):
        self._index_kits_path = index_kits_path
        self._schema_path = schema_path
        self._index_kits = []
        self._load_index_kits()

        self._index_kit_by_name = {ik["Name"]: ik for ik in self._index_kits}

    def _load_index_kits(self):
        self._index_kits = [ik for ik in self._index_kits_path.glob("*.json")]


class IndexKitDefinition:

    def __init__(self, index_json_path: Path, schema_path: Path):

        self._index_import_error = None

        self._index_kit = None
        self._supported_library_prep_kits = None
        self._indices_i7 = None
        self._indices_i5 = None
        self._indices_dual_fixed = None

        with open(schema_path, "r") as schema_fh:
            schema = json.load(schema_fh)

        with open(index_json_path, "r") as index_json_fh:
            indata = json.load(index_json_fh)

        try:
            validate(instance=indata, schema=schema)
        except jsonschema.ValidationError as e:
            self._index_import_error = e
            return

        self._index_kit = indata["index_kit"]
        self._supported_library_prep_kits = indata["supported_library_prep_kits"]
        self._resources = indata["resources"]
        self._indices_i7 = pd.DataFrame.from_dict(indata["indices_i7"])
        self._indices_i5 = pd.DataFrame.from_dict(indata["indices_i5"])
        self._indices_dual_fixed = pd.DataFrame.from_dict(indata["indices_dual_fixed"])

        self._add_extra_data(self._indices_i7)
        self._add_extra_data(self._indices_i5)
        self._add_extra_data(self._indices_dual_fixed)

    def _add_extra_data(self, idx_df: pd.DataFrame):
        if "adapter" in self._resources:
            idx_df["adapter_read1"] = self._resources["adapter"]
        if "adapter_read2" in self._resources:
            idx_df["adapter_read2"] = self._resources["adapter_read2"]
        if "name" in self._index_kit:
            idx_df["index_kit_definition_name"] = self._index_kit["name"]
        if "override_cycles_pattern" in self._index_kit:
            idx_df["override_cycles_pattern"] = self._index_kit[
                "override_cycles_pattern"
            ]

    def has_indices_dual_fixed(self) -> bool:
        return not self._indices_dual_fixed.empty

    def has_indices_i7(self) -> bool:
        return not self._indices_i7.empty

    def has_indices_i5(self) -> bool:
        return not self._indices_i5.empty

    def is_valid(self) -> bool:
        if self._index_import_error:
            return False

        return True

    def indices_i7(self) -> pd.DataFrame:
        return self._indices_i7

    def indices_i5(self) -> pd.DataFrame:
        return self._indices_i5

    def indices_dual_fixed(self) -> pd.DataFrame:
        return self._indices_dual_fixed

    def name(self) -> str:
        return self._index_kit["name"]

    def overridecycles_pattern(self) -> str:
        return self._index_kit["overridecycles_pattern"]


#
#
# def run_import():
#     index_root = Path(r'C:\Dev\PyCharmProjects\SampleSheetCreator\config\indexes\data')
#     index_schema = Path(r'C:\Dev\PyCharmProjects\SampleSheetCreator\config\indexes\schema.json')
#
#     jsons = index_root.glob('*.json')
#
#     for j in jsons:
#
#         obj = IndexKitDefinition(j, index_schema)
#
#         # print("import error:", obj._index_import_error)
#         # print("override_pattern:", obj._overridecycles_pattern)
#         # print("index_kit:", obj._index_kit)
#         # print("supported_library_prep_kits:", obj._supported_library_prep_kits)
#         # print("indices_i7:", obj._indices_i7)
#         # print("indices_i5:", obj._indices_i5)
#         # print("indices_dual_fixed", obj._indices_dual_fixed)
#
#         run_cycles = {
#             'rd1': 151,
#             'ix1': 10,
#             'ix2': 10,
#             'rd2': 151
#         }
#
#         outstr = obj._overridecycles_pattern.format(**run_cycles)
#
# def run_convert():
#     index_root = Path(r'C:\Dev\PyCharmProjects\SampleSheetCreator\config\indexes\Illumina_UDI')
#     out_root = Path(r'C:\Dev\PyCharmProjects\SampleSheetCreator\config\indexes\data')
#
#     tsvs = index_root.glob('*.tsv')
#
#     for t in tsvs:
#         fn = t.name
#         _outfile = out_root / fn
#         outfile = _outfile.with_suffix(".json")
#
#         obj = IlluminaFormatIndexKitDefinition(t)
#         obj.save_json(outfile)
#
#
# if __name__ == '__main__':
#     run_convert()
