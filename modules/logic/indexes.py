import pandas as pd
from io import StringIO
from camel_converter import to_snake
from pathlib import Path


class IndexKitDefinition:
    strategies = ("NoIndex", "SingleOnly", "DualOnly", "SingleAndDual", "NoAndSingle", "NoAndDual", "All")
    required_sections = ("IndexKit", "Resources", "Indices", "SupportedLibraryPrepKits")

    def __init__(self, index_file: Path):
        self.index_file = index_file
        self.indexes_all = pd.DataFrame()
        self.resources = []
        self.supported_library_prep_kits = []
        self.f_positions = pd.DataFrame()
        self.indexes_i7 = pd.DataFrame()
        self.indexes_i5 = pd.DataFrame()
        self.fixed_indexes = pd.DataFrame()

        if self.validate():
            self.valid = True
            self.parse_index_file()
        else:
            self.valid = False

        self.has_fixed_indexes = True if not self.fixed_indexes.empty else False
        self.has_i7_indexes = True if not self.indexes_i7.empty else False
        self.has_i5_indexes = True if not self.indexes_i5.empty else False

    def validate(self) -> bool:
        sections = {}
        current_section = None

        try:
            content = self.index_file.read_text(encoding="utf-8")

            for line in content.splitlines():
                line = line.strip()

                if not line:
                    continue

                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    sections[current_section] = []
                else:
                    sections[current_section].append(line)

        except Exception as e:
            return False

        for section in self.required_sections:
            if section not in sections:
                return False

        return True

    def parse_index_file(self):
        sections = {}
        current_section = None

        content = self.index_file.read_text(encoding="utf-8")

        for line in content.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                sections[current_section] = []
            else:
                sections[current_section].append(line)

        if 'IndexKit' in sections:
            for line in sections['IndexKit']:
                key, value = line.strip().split('\t')
                setattr(self, to_snake(key), value)

        elif 'Kit' in sections:
            for line in sections['Kit']:
                key, value = line.strip().split('\t')
                setattr(self, to_snake(key), value)

        if 'Resources' in sections:
            resources_content = '\n'.join(sections['Resources'])
            self.resources = pd.read_csv(StringIO(resources_content), sep='\t', header=0)
            self.process_resources()

        if 'Indices' in sections:
            indexes_content = '\n'.join(sections['Indices'])
            self.indexes_all = pd.read_csv(StringIO(indexes_content), sep='\t', header=0)
            self.process_indexes()

        if 'SupportedLibraryPrepKits' in sections:
            self.supported_library_prep_kits = sections['SupportedLibraryPrepKits']

    def process_resources(self):
        _meta = self.resources[self.resources['Type'] != 'FixedIndexPosition']

        print(_meta.to_string())

        for row in _meta.itertuples():
            setattr(self, to_snake(row.Name), row.Value)

        if hasattr(self, "fixed_layout"):
            setattr(self, "fixed_layout", self._to_boolean(self.fixed_layout))

        _fixed_index_positions = self.resources[self.resources['Type'] == 'FixedIndexPosition'].copy()
        self.f_positions = _fixed_index_positions[["Name", "Value"]]

    def process_indexes(self):
        _indexes_i7 = self.indexes_all[self.indexes_all['IndexReadNumber'] == 1].copy()
        _indexes_i7 = _indexes_i7.rename(columns={"Sequence": "Index_I7", "Name": "Name_I7"})
        _indexes_i7 = _indexes_i7.drop(columns=['IndexReadNumber']).reset_index()

        _indexes_i5 = self.indexes_all[self.indexes_all['IndexReadNumber'] == 2].copy()
        _indexes_i5 = _indexes_i5.rename(columns={"Sequence": "Index_I5", "Name": "Name_I5"})
        _indexes_i5 = _indexes_i5.drop(columns=['IndexReadNumber']).reset_index()

        if not _indexes_i7.empty:
            self.indexes_i7 = _indexes_i7
            self.indexes_i7.drop(["index"], axis=1, inplace=True)

        if not _indexes_i5.empty:
            self.indexes_i5 = _indexes_i5
            self.indexes_i5.drop(["index"], axis=1, inplace=True)

        if not self.f_positions.empty:
            _f_indexes = self.f_positions.copy()
            _f_indexes.rename(columns={'Name': 'FixedPos'}, inplace=True)
            _f_indexes[['Name_I7', 'Name_I5']] = _f_indexes['Value'].str.split(pat='-', expand=True)
            _f_indexes = _f_indexes.drop('Value', axis=1)

            if not _indexes_i7.empty:
                _f_indexes = pd.merge(_f_indexes, _indexes_i7, on='Name_I7', how='outer')

            if not _indexes_i5.empty:
                _f_indexes = pd.merge(_f_indexes, _indexes_i5, on='Name_I5', how='outer')

            self.fixed_indexes = _f_indexes

        if hasattr(self, "adapter"):
            self.indexes_i5['AdapterRead1'] = self.adapter
            self.indexes_i7['AdapterRead1'] = self.adapter
            self.fixed_indexes['AdapterRead1'] = self.adapter
            self.indexes_i5['AdapterRead2'] = self.adapter
            self.indexes_i7['AdapterRead2'] = self.adapter
            self.fixed_indexes['AdapterRead2'] = self.adapter

        if hasattr(self, "adapter_read2"):
            self.indexes_i5['AdapterRead2'] = self.adapter_read2
            self.indexes_i7['AdapterRead2'] = self.adapter_read2
            self.fixed_indexes['AdapterRead2'] = self.adapter_read2



    @staticmethod
    def _to_boolean(value):
        value_lower = value.lower()
        if value_lower == "true":
            return True
        elif value_lower == "false":
            return False
        else:
            return None
