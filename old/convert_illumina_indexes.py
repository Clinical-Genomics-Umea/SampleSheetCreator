import argparse
import ast

from pathlib import Path
from dataclasses import dataclass, field
from typing import List
import pandas as pd
from io import StringIO
from Bio.Seq import Seq
from camel_converter import to_snake


def rc(seq):
    return str(Seq(seq).reverse_complement())


class IndexKitDefinition:
    def __init__(self, index_file: Path):
        self.index_file: index_file

        self.strategies = ("NoIndex", "SingleOnly", "DualOnly", "SingleAndDual", "NoAndSingle", "NoAndDual", "All")

        index_kit: dict = field(init=False)
        resources: pd.DataFrame = field(init=False)
        indexes_all: pd.DataFrame = field(init=False)
        supported_library_prep_kits: list = field(init=False)

        # def default_strategies_list(self) -> List[str]:
        #     return ["NoIndex", "SingleOnly", "DualOnly", "SingleAndDual", "NoAndSingle", "NoAndDual", "All"]

    def validate(self):

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
            print(e)
            return False

        for section in ["IndexKit", "Resources", "Indices", "SupportedLibraryPrepKits"]:
            if section not in sections:
                print(f"Section '{section}' not found in the index kit definition file.")
                return False

        return True

    def __post_init__(self) -> None:

        if self.validate():
            setattr(self, "valid", True)
            self.parse_index_file()

        else:
            setattr(self, "valid", False)


    def get_plate_pos(self) -> pd.DataFrame:
        i5_indexes = (
            self.indexes_all[self.indexes_all['IndexReadNumber'] == 1]
            .rename(columns={"Sequence": "Sequence_I5", "Name": "Name_I5"})
            .drop(columns=['IndexReadNumber'])
        )

        i7_indexes = (
            self.indexes_all[self.indexes_all['IndexReadNumber'] == 2]
            .rename(columns={"Sequence": "Sequence_I7", "Name": "Name_I7"})
            .drop(columns=['IndexReadNumber'])
        )

        plate_pos = self.resources[self.resources['Type'] == 'FixedIndexPosition'].copy()
        plate_pos.rename(columns={'Name': 'PlatePos'}, inplace=True)
        plate_pos[['Name_I7', 'Name_I5']] = plate_pos['Value'].str.split(pat='-', expand=True)
        plate_pos = plate_pos.drop(['Value', 'Type', 'Format', 'LibraryPrepKits'], axis=1)

        plate_pos = pd.merge(plate_pos, i7_indexes, on='Name_I7', how='outer')
        plate_pos = pd.merge(plate_pos, i5_indexes, on='Name_I5', how='outer')

        plate_pos['Sequence_I5_rc'] = plate_pos['Sequence_I5'].apply(lambda x: rc(x))

        return plate_pos

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
                line = line.strip()
                k, v = line.split('\t')
                setattr(self, to_snake(k), v)

        if 'Kit' in sections:
            for line in sections['Kit']:
                line = line.strip()
                k, v = line.split('\t')
                setattr(self, to_snake(k), v)

        if 'Resources' in sections:
            self.resources = pd.read_csv(StringIO('\n'.join(sections['Resources'])), sep='\t', header=0)
            self.process_resources()

        if 'Indices' in sections:
            self.indexes_all = pd.read_csv(StringIO('\n'.join(sections['Indices'])), sep='\t', header=0)
            self.process_indexes()

        if 'SupportedLibraryPrepKits' in sections:
            self.supported_library_prep_kits = sections['SupportedLibraryPrepKits']

    def process_resources(self):
        _meta = self.resources[self.resources['Type'] != 'FixedIndexPosition']
        for row in _meta.itertuples():
            setattr(self, to_snake(row.Name), row.Value)

        if hasattr(self, "fixed_layout"):
            setattr(self, "fixed_layout", self.convert_to_boolean(self.fixed_layout))

        fixed_index_positions = self.resources[self.resources['Type'] == 'FixedIndexPosition'].copy()
        setattr(self, "fixed_index_positions", fixed_index_positions[["Name", "Value"]])

    def process_indexes(self):
        indexes_i7 = (
            self.indexes_all[self.indexes_all['IndexReadNumber'] == 1]
            .rename(columns={"Sequence": "Sequence_I7", "Name": "Name_I7"})
            .drop(columns=['IndexReadNumber'])
        )

        indexes_i5 = (
            self.indexes_all[self.indexes_all['IndexReadNumber'] == 2]
            .rename(columns={"Sequence": "Sequence_I5", "Name": "Name_I5"})
            .drop(columns=['IndexReadNumber'])
        )

        if not indexes_i7.empty:
            setattr(self, "indexes_i7", indexes_i7)

        if not indexes_i5.empty:
            setattr(self, "indexes_i5", indexes_i5)

        if not indexes_i5.empty and not indexes_i7.empty and not self.fixed_index_positions.empty:
            pos_indexes = self.fixed_index_positions.copy()
            pos_indexes.rename(columns={'Name': 'Pos'}, inplace=True)
            pos_indexes[['Name_I7', 'Name_I5']] = pos_indexes['Value'].str.split(pat='-', expand=True)
            pos_indexes = pos_indexes.drop('Value', axis=1)

            pos_indexes = pd.merge(pos_indexes, indexes_i7, on='Name_I7', how='outer')
            pos_indexes = pd.merge(pos_indexes, indexes_i5, on='Name_I5', how='outer')

            setattr(self, "pos_indexes", pos_indexes)


    @staticmethod
    def convert_to_boolean(value):
        value_lower = value.lower()
        if value_lower == "true":
            return True
        elif value_lower == "false":
            return False
        else:
            return None


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ilmn_index_file', type=str, required=True,
                        help='Illumina local run manager index file')

    args = parser.parse_args()
    index_path = Path(args.ilmn_index_file)

    index_data = IndexKitDefinition(index_path)
    # #
    print(index_data.valid)


if __name__ == "__main__":
    main()
