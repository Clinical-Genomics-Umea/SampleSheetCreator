from pathlib import Path
import json
from io import StringIO

import pandas as pd
from camel_converter import to_snake


class IlluminaFormatIndexKitDefinition:

    def __init__(self, ilmn_index_file_path: Path,
                 override_cycles_pattern="Y$r1-I$i1-I$i2-Y$r2"):

        self.overridecycles_pattern = None
        self.index_kit = None
        self.supported_library_prep_kits = None
        self.resources = None
        self.indices_i7 = None
        self.indices_i5 = None
        self.indices_dual_fixed = None
        self.index_import_error = None

        self.indata = dict()

        self.ingest_index_file(ilmn_index_file_path)

        self.index_kit = self.indata['index_kit']
        self.index_kit['override_cycles_pattern'] = override_cycles_pattern
        self.supported_library_prep_kits = self.indata['supported_library_prep_kits']

        self.indices_i7 = (self.indata['indices'][self.indata['indices']['index_read_number'] == 1]
                           .copy()
                           .rename(columns={"name": "index_i7_name", "sequence": "index_i7"})
                           .drop(columns=['index_read_number'])
                           .reset_index(drop=True)
                           )

        self.indices_i5 = (self.indata['indices'][self.indata['indices']['index_read_number'] == 2]
                           .copy()
                           .rename(columns={"name": "index_i5_name", "sequence": "index_i5"})
                           .drop(columns=['index_read_number'])
                           .reset_index(drop=True)
                           )

        _other_resources = self.indata['resources'][
            ~self.indata['resources']['type'].str.contains('FixedIndexPosition')].copy()
        _other_resources['snake_name'] = _other_resources['name'].apply(to_snake)
        self.resources = dict(zip(_other_resources['snake_name'], _other_resources['value']))

        if self.index_kit['index_strategy'] == "DualOnly" and self.indata['resources']['type'].str.contains(
                'FixedIndexPosition').any():
            _idxs_dual_fix_ = self.indata['resources'][
                self.indata['resources']['type'].str.contains('FixedIndexPosition')]

            _idxs_dual_fix_ = _idxs_dual_fix_.rename(columns={'name': 'fixed_pos'})
            _idxs_dual_fix_[['index_i7_name', 'index_i5_name']] = _idxs_dual_fix_['value'].str.split('-',
                                                                                                     expand=True)
            _idxs_dual_fix_ = _idxs_dual_fix_.drop(columns=['type', 'format', 'value']).reset_index(
                drop=True)

            self.indices_dual_fixed = (_idxs_dual_fix_.merge(self.indices_i7, on='index_i7_name')
                                       .merge(self.indices_i5, on='index_i5_name')
                                       .copy())

    def ingest_index_file(self, index_file):
        sections = {}
        current_section = None

        resources_orig_header = ["Name", "Type", "Format", "Value"]
        resources_snake_header_dict = {x: to_snake(x) for x in resources_orig_header}
        resources_snake_header = list(resources_snake_header_dict.values())

        indices_orig_header = ["Name", "Sequence", "IndexReadNumber"]
        indices_snake_header_dict = {x: to_snake(x) for x in indices_orig_header}
        indices_snake_header = list(indices_snake_header_dict.values())

        content = index_file.read_text(encoding="utf-8")

        for line in content.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                sections[current_section] = []
            else:
                sections[current_section].append(line)

        if 'IndexKit' in sections or 'Kit' in sections:
            self.indata['index_kit'] = {to_snake(key): value for key, value in
                                        (row.strip().split('\t') for row in sections['IndexKit'])}

        if 'SupportedLibraryPrepKits' in sections:
            self.indata['supported_library_prep_kits'] = [row.strip() for row in sections['SupportedLibraryPrepKits']]

        if 'Resources' in sections:
            resources_content = '\n'.join(sections['Resources'])

            self.indata['resources'] = pd.read_csv(StringIO(resources_content), sep='\t', header=0)
            self.indata['resources'] = self.indata['resources'].rename(columns=resources_snake_header_dict).copy()
            self.indata['resources'] = self.indata['resources'][resources_snake_header].copy()

        if 'Indices' in sections:
            indexes_content = '\n'.join(sections['Indices'])
            self.indata['indices'] = pd.read_csv(StringIO(indexes_content), sep='\t', header=0)
            self.indata['indices'] = self.indata['indices'].rename(columns=indices_snake_header_dict).copy()
            self.indata['indices'] = self.indata['indices'][indices_snake_header].copy()

    def _make_output_dict(self):
        data = {
            'index_kit': self.index_kit,
            'resources': self.resources,
            'indices_i7': self._df_to_json_compat(self.indices_i7),
            'indices_i5': self._df_to_json_compat(self.indices_i5),
            'indices_dual_fixed': self._df_to_json_compat(self.indices_dual_fixed),
            'supported_library_prep_kits': self.supported_library_prep_kits
        }

        return data

    @staticmethod
    def _df_to_json_compat(data):
        if isinstance(data, pd.DataFrame):
            return data.to_dict(orient='records')
        if data is None:
            return pd.DataFrame().to_dict(orient='records')

    def save_json(self, path):
        with open(path, 'w') as f:
            json.dump(self._make_output_dict(), f, indent=4)

        return "saved"
