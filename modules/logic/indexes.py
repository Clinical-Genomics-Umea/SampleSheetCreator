from functools import reduce

import pandas as pd
from io import StringIO
from pathlib import Path
import json
import jsonschema
from jsonschema import validate


class IndexKitDefinition:

    def __init__(self, index_json_path: Path, schema_path: Path):

        self.index_import_error = None

        self.overridecycles_pattern = None
        self.index_kit = None
        self.supported_library_prep_kits = None
        self.indices_i7 = None
        self.indices_i5 = None
        self.indices_dual_fixed = None
        self.supported_library_prep_kits = None

        with open(schema_path, 'r') as f:
            schema = json.load(f)

        with open(index_json_path, 'r') as f:
            indata = json.load(f)

        try:
            validate(instance=indata, schema=schema)
        except jsonschema.ValidationError as e:
            print(e)
            self.index_import_error = e
            return

        if 'overridecycles_pattern' in indata:
            self.overridecycles_pattern = indata['overridecycles_pattern']
        if 'index_kit' in indata:
            self.index_kit = indata['index_kit']
        if 'supported_library_prep_kits' in indata:
            self.supported_library_prep_kits = indata['supported_library_prep_kits']
        if 'indices_i7' in indata:
            self.indices_i7 = pd.DataFrame.from_dict(indata['indices_i7'])
        if 'indices_i5' in indata:
            self.indices_i5 = pd.DataFrame.from_dict(indata['indices_i5'])
        if 'indices_dual_fixed' in indata:
            self.indices_dual_fixed = pd.DataFrame.from_dict(indata['indices_dual_fixed'])


class IlluminaFormatIndexKitDefinition:

    def __init__(self, ilmn_index_file_path: Path,
                 overridecycles_pattern="Y<read1_len>;I<index1_len>;I<index2_len>;Y<read2_len>"):

        self.overridecycles_pattern = overridecycles_pattern

        self.indata = dict()

        self.fixed_index_position = pd.DataFrame()
        self.index_read1 = pd.DataFrame()
        self.index_read2 = pd.DataFrame()
        self.fixed_dual_indexes = pd.DataFrame()

        self.ingest_index_file(ilmn_index_file_path)

        self.index_kit = self.indata['index_kit']
        self.supported_library_prep_kits = self.indata['supported_library_prep_kits']

        self.indices_i7 = (self.indata['indices'][self.indata['indices']['IndexReadNumber'] == 1]
                           .copy()
                           .rename(columns={"Sequence": "IndexI7", "Name": "IndexI7Name"})
                           .drop(columns=['IndexReadNumber'])
                           .reset_index(drop=True)
                           )

        self.indices_i5 = (self.indata['indices'][self.indata['indices']['IndexReadNumber'] == 2]
                           .copy()
                           .rename(columns={"Name": "IndexI5Name", "Sequence": "IndexI5"})
                           .drop(columns=['IndexReadNumber'])
                           .reset_index(drop=True)
                           )

        _other_resources = self.indata['resources'][
            ~self.indata['resources']['Type'].str.contains('FixedIndexPosition')]
        self.resources = dict(zip(_other_resources['Name'], _other_resources['Value']))

        if self.index_kit['IndexStrategy'] == "DualOnly" and self.indata['resources']['Type'].str.contains(
                'FixedIndexPosition').any():
            _idxs_dual_fix_ = self.indata['resources'][
                self.indata['resources']['Type'].str.contains('FixedIndexPosition')]
            _idxs_dual_fix_ = _idxs_dual_fix_.rename(columns={'Name': 'FixedPos'})
            _idxs_dual_fix_[['IndexI7Name', 'IndexI5Name']] = _idxs_dual_fix_['Value'].str.split('-',
                                                                                                 expand=True)
            _idxs_dual_fix_ = _idxs_dual_fix_.drop(columns=['Type', 'Format', 'Value']).reset_index(
                drop=True)

            self.indices_dual_fixed = (_idxs_dual_fix_.merge(self.indices_i7, on='IndexI7Name')
                                       .merge(self.indices_i5, on='IndexI5Name').copy())

    def ingest_index_file(self, index_file):
        sections = {}
        current_section = None

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
            self.indata['index_kit'] = {key: value for key, value in
                                        (row.strip().split('\t') for row in sections['IndexKit'])}

        if 'SupportedLibraryPrepKits' in sections:
            self.indata['supported_library_prep_kits'] = [row.strip() for row in sections['SupportedLibraryPrepKits']]

        if 'Resources' in sections:
            resources_content = '\n'.join(sections['Resources'])
            self.indata['resources'] = pd.read_csv(StringIO(resources_content), sep='\t', header=0)
            self.indata['resources'] = self.indata['resources'][["Name", "Type", "Format", "Value"]].copy()

        if 'Indices' in sections:
            indexes_content = '\n'.join(sections['Indices'])
            self.indata['indices'] = pd.read_csv(StringIO(indexes_content), sep='\t', header=0)
            self.indata['indices'] = self.indata['indices'][["Name", "Sequence", "IndexReadNumber"]].copy()

    def to_dict(self):
        data = {
            'overridecycles_pattern': self.overridecycles_pattern,
            'index_kit': self.index_kit,
            'resources': self.resources,
            'indices_i7': self.indices_i7.to_dict(orient='records'),
            'indices_i5': self.indices_i5.to_dict(orient='records'),
            'supported_library_prep_kits': self.supported_library_prep_kits
        }

        if not self.fixed_dual_indexes.empty:
            data['fixed_dual_indexes'] = self.fixed_dual_indexes.to_dict(orient='records')


        return data

    def save_json(self, path):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

#
# class IndexKitDefinition:
#     strategies = ("NoIndex", "SingleOnly", "DualOnly", "SingleAndDual", "NoAndSingle", "NoAndDual", "All")
#     required_sections = ("IndexKit", "Resources", "Indices", "SupportedLibraryPrepKits")
#
#     def __init__(self, index_file: Path):
#         self.index_file = index_file
#         self.indexes_all = pd.DataFrame()
#         self.resources = []
#         self.supported_library_prep_kits = []
#         self.f_positions = pd.DataFrame()
#         self.indexes_i7 = pd.DataFrame()
#         self.indexes_i5 = pd.DataFrame()
#         self.fixed_indexes = pd.DataFrame()
#         self.umi_read1 = None
#         self.umi_read2 = None
#
#         if self.validate():
#             self.valid = True
#             self.parse_index_file()
#         else:
#             self.valid = False
#
#         self.has_fixed_indexes = True if not self.fixed_indexes.empty else False
#         self.has_i7_indexes = True if not self.indexes_i7.empty else False
#         self.has_i5_indexes = True if not self.indexes_i5.empty else False
#
#     def validate(self) -> bool:
#         sections = {}
#         current_section = None
#
#         try:
#             content = self.index_file.read_text(encoding="utf-8")
#
#             for line in content.splitlines():
#                 line = line.strip()
#
#                 if not line:
#                     continue
#
#                 if line.startswith('[') and line.endswith(']'):
#                     current_section = line[1:-1]
#                     sections[current_section] = []
#                 else:
#                     sections[current_section].append(line)
#
#         except Exception as e:
#             return False
#
#         for section in self.required_sections:
#             if section not in sections:
#                 return False
#
#         return True
#
#     def parse_index_file(self):
#         sections = {}
#         current_section = None
#
#         content = self.index_file.read_text(encoding="utf-8")
#
#         for line in content.splitlines():
#             line = line.strip()
#
#             if not line:
#                 continue
#
#             if line.startswith('[') and line.endswith(']'):
#                 current_section = line[1:-1]
#                 sections[current_section] = []
#             else:
#                 sections[current_section].append(line)
#
#         if 'IndexKit' in sections:
#             for line in sections['IndexKit']:
#                 key, value = line.strip().split('\t')
#                 setattr(self, to_snake(key), value)
#
#         elif 'Kit' in sections:
#             for line in sections['Kit']:
#                 key, value = line.strip().split('\t')
#                 setattr(self, to_snake(key), value)
#
#         if 'Resources' in sections:
#             resources_content = '\n'.join(sections['Resources'])
#             self.resources = pd.read_csv(StringIO(resources_content), sep='\t', header=0)
#             self.process_resources()
#
#         if 'Indices' in sections:
#             indexes_content = '\n'.join(sections['Indices'])
#             self.indexes_all = pd.read_csv(StringIO(indexes_content), sep='\t', header=0)
#             self.process_indexes()
#
#         if 'SupportedLibraryPrepKits' in sections:
#             self.supported_library_prep_kits = sections['SupportedLibraryPrepKits']
#
#     def process_resources(self):
#         _meta = self.resources[self.resources['Type'] != 'FixedIndexPosition']
#
#         print(_meta.to_string())
#
#         for row in _meta.itertuples():
#             setattr(self, to_snake(row.Name), row.Value)
#
#         if hasattr(self, "fixed_layout"):
#             setattr(self, "fixed_layout", self._to_boolean(self.fixed_layout))
#
#         _fixed_index_positions = self.resources[self.resources['Type'] == 'FixedIndexPosition'].copy()
#         self.f_positions = _fixed_index_positions[["Name", "Value"]]
#
#     def process_indexes(self):
#         _indexes_i7 = self.indexes_all[self.indexes_all['IndexReadNumber'] == 1].copy()
#         _indexes_i7 = _indexes_i7.rename(columns={"Sequence": "Index_I7", "Name": "Name_I7"})
#         _indexes_i7 = _indexes_i7.drop(columns=['IndexReadNumber']).reset_index()
#
#         _indexes_i5 = self.indexes_all[self.indexes_all['IndexReadNumber'] == 2].copy()
#         _indexes_i5 = _indexes_i5.rename(columns={"Sequence": "Index_I5", "Name": "Name_I5"})
#         _indexes_i5 = _indexes_i5.drop(columns=['IndexReadNumber']).reset_index()
#
#         if not _indexes_i7.empty:
#             self.indexes_i7 = _indexes_i7
#             self.indexes_i7.drop(["index"], axis=1, inplace=True)
#
#         if not _indexes_i5.empty:
#             self.indexes_i5 = _indexes_i5
#             self.indexes_i5.drop(["index"], axis=1, inplace=True)
#
#         if not self.f_positions.empty:
#             _f_indexes = self.f_positions.copy()
#             _f_indexes.rename(columns={'Name': 'FixedPos'}, inplace=True)
#             _f_indexes[['Name_I7', 'Name_I5']] = _f_indexes['Value'].str.split(pat='-', expand=True)
#             _f_indexes = _f_indexes.drop('Value', axis=1)
#
#             if not _indexes_i7.empty:
#                 _f_indexes = pd.merge(_f_indexes, _indexes_i7, on='Name_I7', how='outer')
#
#             if not _indexes_i5.empty:
#                 _f_indexes = pd.merge(_f_indexes, _indexes_i5, on='Name_I5', how='outer')
#
#             self.fixed_indexes = _f_indexes
#
#         if hasattr(self, "adapter"):
#             self.indexes_i5['AdapterRead1'] = self.adapter
#             self.indexes_i7['AdapterRead1'] = self.adapter
#             self.fixed_indexes['AdapterRead1'] = self.adapter
#             self.indexes_i5['AdapterRead2'] = self.adapter
#             self.indexes_i7['AdapterRead2'] = self.adapter
#             self.fixed_indexes['AdapterRead2'] = self.adapter
#
#         if hasattr(self, "adapter_read2"):
#             self.indexes_i5['AdapterRead2'] = self.adapter_read2
#             self.indexes_i7['AdapterRead2'] = self.adapter_read2
#             self.fixed_indexes['AdapterRead2'] = self.adapter_read2
#
#     @staticmethod
#     def _to_boolean(value):
#         value_lower = value.lower()
#         if value_lower == "true":
#             return True
#         elif value_lower == "false":
#             return False
#         else:
#             return None


if __name__ == '__main__':
    index_root = Path(r'C:\Dev\PyCharmProjects\SampleSheetCreator\config\indexes\Illumina_UDI')
    index_json_root = Path(r'C:\Dev\PyCharmProjects\SampleSheetCreator\demo\indexes_json')

    tsvs = index_root.glob('*.tsv')

    for tsv in tsvs:

        fn = tsv.name
        outfile = index_json_root / fn
        outfile = outfile.with_suffix('.json')
        print(outfile)

        obj = IlluminaFormatIndexKitDefinition(tsv)
        print(obj.save_json(outfile))

