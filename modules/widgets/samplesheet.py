from dataclasses import dataclass
import pandas as pd
import pandera as pa
import json
import re
from string import Template
from functools import partial

class SampleSheetV2:
    def __init__(self, header: dict = None, run_cycles: dict = None,
                 sequencing_data: dict = None, sample_df: pd.DataFrame = None):

        self.standalone = dict()
        self.application = dict()

        self.standalone['Header'] = Header(header)
        self.standalone['Reads'] = Reads(run_cycles)

        reads_data = self.standalone['Reads'].data

        if sequencing_data is not None:
            self.standalone['Sequencing'] = Sequencing(sequencing_data)

        if sample_df is None:
            sample_df = pd.DataFrame()

        override_adder = partial(self.override_cycles, run_cycles=run_cycles)
        sample_df['OverrideCycles'] = sample_df.apply(lambda row: override_adder(row['IndexI7'],
                                                                                 row['IndexI5'],
                                                                                 row['OverrideCyclesPattern']),
                                                      axis=1)

        self.application['BCLConvert'] = BCLConvert(sample_df)

        used_applications = sample_df['Application'].unique()
        for app in used_applications:
            df_subset = sample_df[sample_df['Application'] == app]
            self.application[app] = Application(df_subset)

    def datalist(self):

        datalist = []

        for app in self.standalone:
            datalist.extend(self.standalone[app].datalist())

        for app in self.application:
            datalist.extend(self.application[app].datalist())

        return datalist

    def _fill_i1_pat(self, i1_pat, i1_len, runcycles):
        placeholder = "ix1"
        pattern = r'([A-Z])(\d+)'
        matches = re.findall(pattern, i1_pat)
        known_sum = 0

        for match in matches:
            known_sum += int(match[1])

        # placeholder_value = runcycles - known_sum
        placeholder_value = i1_len
        tot_index_cycles = i1_len + known_sum
        empty_index_cycles = runcycles - tot_index_cycles

        if empty_index_cycles > 0:
            i1_pat = f"N{empty_index_cycles}{i1_pat}"

        t = Template(i1_pat)
        completed_str = t.substitute({placeholder: placeholder_value})
        return completed_str

    def override_cycles(self, index, index2, override_cycles_pattern, run_cycles):

        r1, i1, i2, r2 = run_cycles.split('-')
        r1_runc, i1_runc, i2_runc, r2_runc = int(r1), int(i1), int(i2), int(r2)

        r1_runc, i1_runc, i2_runc, r2_runc = 171, 8, 8, 171

        i1_len = len(index)
        i2_len = len(index2)

        r1_pat, i1_pat, i2_pat, r2_pat = override_cycles_pattern.split('-')

        r1_str = self._fill_oc_read('$r1', r1_pat, r1_runc)
        i1_str = self._n_pad_right('$i1', i1_pat, i1_len, i1_runc)
        i2_str = self._n_pad_left('$i2', i2_pat, i2_len, i2_runc)
        r2_str = self._fill_oc_read('$r2', r2_pat, r2_runc)

        return f"{r1_str};{i1_str};{i2_str};{r2_str}"


    @staticmethod
    def _validate(s):
        pattern_r = r'([A-Z]\d+)+'
        return bool(re.fullmatch(pattern_r, s))

    @staticmethod
    def _get_known_len(matches):
        known_len = 0
        for match in matches:
            known_len += int(match[1])

        return known_len

    def _fill_oc_read(self, placeholder, oc_pattern, runcycles):

        oc_pattern_replaced = oc_pattern.replace(placeholder, str(0))

        pattern = r'([A-Z])(\d+)'

        if not self._validate(oc_pattern_replaced):
            return "invalid oc pattern"

        matches = re.findall(pattern, oc_pattern_replaced)
        matches = [list(t) for t in matches]

        known_len = self._get_known_len(matches)

        if known_len == runcycles:
            return oc_pattern_replaced

        if known_len < runcycles:
            unaccounted_cycles = runcycles - known_len

            for match in matches:
                if match[0] == "Y":
                    match[1] = str(int(match[1]) + unaccounted_cycles)

            oc_pattern_replaced_updated = "".join([match[0] + match[1] for match in matches])

            return oc_pattern_replaced_updated

    def _n_pad_left(self, placeholder, oc_pattern, index_len, runcycles):

        oc_pattern_replaced = oc_pattern.replace(placeholder, str(index_len))

        pattern = r'([A-Z])(\d+)'

        if index_len > runcycles:
            return "index_len > runcycles"

        if not self._validate(oc_pattern_replaced):
            return "invalid oc pattern"

        matches = re.findall(pattern, oc_pattern_replaced)
        matches = [list(t) for t in matches]
        known_len = self._get_known_len(matches)

        if known_len == runcycles:
            return oc_pattern_replaced

        if known_len < runcycles:
            unaccounted_cycles = runcycles - known_len
            if not matches[0][0] == "N":
                matches.insert(0, ("N", str(unaccounted_cycles)))
            else:
                accounted_n_left = int(matches[0][1])
                updated_accounted_n_left = accounted_n_left + unaccounted_cycles
                matches[0] = [matches[0][0], str(updated_accounted_n_left)]

            oc_pattern_replaced_updated = "".join([match[0] + match[1] for match in matches])

            return oc_pattern_replaced_updated

    def _n_pad_right(self, placeholder, oc_pattern, index_len, runcycles):
        oc_pattern_replaced = oc_pattern.replace(placeholder, str(index_len))

        pattern = r'([A-Z])(\d+)'

        if index_len > runcycles:
            return "index_len > runcycles"

        if not self._validate(oc_pattern_replaced):
            return "invalid oc pattern"

        matches = re.findall(pattern, oc_pattern_replaced)
        known_len = self._get_known_len(matches)

        if known_len == runcycles:
            return oc_pattern_replaced

        if known_len < runcycles:
            unaccounted_cycles = runcycles - known_len
            if not matches[-1][0] == "N":
                matches.append(("N", str(unaccounted_cycles)))
            else:
                accounted_n_right = int(matches[-1][1])
                updated_accounted_n_right = accounted_n_right + unaccounted_cycles
                matches[-1] = [matches[-1][0], str(updated_accounted_n_right)]

            oc_pattern_replaced_updated = "".join([match[0] + match[1] for match in matches])

            return oc_pattern_replaced_updated


class Sequencing:
    def __init__(self, sequencing_data):
        self.header = "[Sequencing]"
        self.data = sequencing_data

    def datalist(self):
        output = list()

        output.append(self.header)
        for key, value in self.data.items():
            output.append(f"{key},{value}")

        output.append("")

        return output


class Header:
    def __init__(self, headerdict):
        self.header = "[Header]"
        self.data = headerdict

    def datalist(self):
        output = list()

        output.append(self.header)
        for key, value in self.data.items():
            output.append(f"{key},{value}")

        output.append("")

        return output


class Reads:
    def __init__(self, run_cycles: dict):
        self.header = "[Reads]"
        self.data = self.extract_reads_data(run_cycles)

    def datalist(self):
        output = list()

        output.append(self.header)
        for key, value in self.data.items():
            output.append(f"{key},{value}")

        output.append("")

        return output

    @staticmethod
    def extract_reads_data(run_cycles: str) -> dict:
        reads_data = dict()

        read1_len, index1_len, index2_len, read2_len = run_cycles.strip().split('-')

        reads_data['Read1Cycles'] = int(read1_len)
        reads_data['Read2Cycles'] = int(index2_len)
        reads_data['Index1Cycles'] = int(index2_len)
        reads_data['Index2Cycles'] = int(read2_len)

        return reads_data


class BCLConvert:
    def __init__(self, df):
        self.app_settings_header = "[BCLConvert_Settings]"
        self.app_data_header = "[BCLConvert_Data]"

        self.app_settings = {
            "SoftwareVersion": df.loc[0, 'SoftwareVersion'],
            "FastqCompressionFormat": df.loc[0, 'FastqCompressionFormat']
        }

        data_fields = ["Sample_ID",
                       "Lane",
                       "Index",
                       "Index2",
                       "AdapterRead1",
                       "AdapterRead2",
                       "BarcodeMismatchesIndex1",
                       "BarcodeMismatchesIndex2",
                       "OverrideCycles"
                       ]

        df.rename(columns={'IndexI7': 'Index', 'IndexI5': 'Index2'}, inplace=True)
        self.data = df[data_fields]

    def datalist(self):

        output = list()

        output.append(self.app_settings_header)
        for key, value in self.app_settings.items():
            output.append(f"{key},{value}")

        output.append("")
        output.append(self.app_data_header)
        output.extend(self.data.to_csv(sep=',', index=False).split("\n"))

        return output

    def validate(self):

        lane8_check = pa.Check.isin([1, 2, 3, 4, 5, 6, 7, 8])
        lane2_check = pa.Check.isin([1, 2])
        dna_check = pa.Check.str_matches(r'^[ACGT]$')
        override_check = pa.Check.str_matches(r'^Y[1-8];I\d+N\d+;N\d+I\d+;Y\d+$')

        data_field_dtypes = pa.DataFrameSchema(
            {
                "Lane": pa.Column(int),
                "Sample_ID": pa.Column(str),
                "index": pa.Column(str),
                "index2": pa.Column(str),
                "AdapterRead1": pa.Column(str),
                "AdapterRead2": pa.Column(str),
                "BarcodeMismatchesIndex1": pa.Column(int),
                "BarcodeMismatchesIndex2": pa.Column(int),
                "OverrideCycles": pa.Column(str)
            },
            index=pa.Index(int),
        )


class Application:
    def __init__(self, df):

        app = df.loc[0, 'Application']
        self.app_settings = json.loads(df.loc[0, 'ApplicationSettings'])
        app_data = json.loads(df.loc[0, 'ApplicationData'])
        data_fields = json.loads(df.loc[0, 'ApplicationDataFields'])

        self.app_settings_header = f"[{app}_Settings]"
        self.app_data_header = f"[{app}_Data]"

        for key, value in app_data.items():
            df[key] = value

        self.data = self.reorder_columns(df[data_fields], "Sample_ID")

    @staticmethod
    def reorder_columns(df, first_column):
        """
        Reorder the columns of a DataFrame such that first_column is the first column
        and second_column is the second column.

        Parameters:
        df (pd.DataFrame): The input DataFrame.
        first_column (str): The name of the column to place first.
        second_column (str): The name of the column to place second.

        Returns:
        pd.DataFrame: The DataFrame with reordered columns.
        """
        # Ensure the specified columns are in the DataFrame
        if first_column not in df.columns:
            raise ValueError("Specified columns must be present in the DataFrame")

        # Get the list of all columns
        all_columns = list(df.columns)

        # Remove the desired columns from the list
        all_columns.remove(first_column)

        # Create the new column order
        new_column_order = [first_column] + all_columns

        # Reorder the DataFrame columns
        df = df[new_column_order]

        return df

    def datalist(self):

        output = list()

        output.append(self.app_settings_header)
        for key, value in self.app_settings.items():

            if isinstance(value, str):
                value = value.lower()

            if isinstance(value, bool):
                value = str(value).lower()

            output.append(f"{key},{value}")

        output.append("")
        output.append(self.app_data_header)
        output.extend(self.data.to_csv(sep=',', index=False).split("\n"))

        return output
