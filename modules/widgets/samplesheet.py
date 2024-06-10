from dataclasses import dataclass
import pandas as pd
import pandera as pa
import json


# def extract_header_data(run_info: dict) -> dict:
#     header_data = run_info['Header']
#
#     instrument_type_to_platform_mapping = {
#         'NextSeq1000': 'NextSeq1000',
#         'NextSeq2000': 'NextSeq2000',
#         'NovaSeqX': 'NovaSeqXSeries'
#     }
#
#     if "InstrumentType" in header_data and "InstrumentPlatform" not in header_data:
#         instrument_type = header_data.get("InstrumentType")
#         platform = instrument_type_to_platform_mapping.get(instrument_type)
#         if platform:
#             header_data["InstrumentPlatform"] = platform
#
#     return header_data
#


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

        override_adder = self.make_override_cycles_adder(reads_data)

        print("sample_df")
        print(sample_df.to_string())
        print("end")


        sample_df['OverrideCycles'] = sample_df.apply(lambda row: override_adder(row['Index_I7'],
                                                                                 row['Index_I5']),
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

    @staticmethod
    def make_override_cycles_adder(run_cycles):

        def add_override_cycles(index, index2):
            len_index = len(str(index))
            len_index2 = len(str(index2))

            read1 = f"Y{run_cycles['Read1Cycles']}"
            read2 = f"Y{run_cycles['Read2Cycles']}"

            i_index1, n_index1 = len_index, run_cycles['Index1Cycles'] - len_index
            i_index2, n_index2 = len_index2, run_cycles['Index2Cycles'] - len_index2
            index1 = f"{i_index1}N{n_index1}" if n_index1 > 0 else f"I{i_index1}"
            index2 = f"N{n_index2}I{i_index2}" if n_index2 > 0 else f"I{i_index2}"

            return f"{read1};{index1};{index2};{read2}"

        return add_override_cycles


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

        df.rename(columns={'Index_I7': 'Index', 'Index_I5': 'Index2'}, inplace=True)
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

        print(df)

        app = df.loc[0, 'Application']
        self.app_settings = json.loads(df.loc[0, 'ApplicationSettings'])
        app_data = json.loads(df.loc[0, 'ApplicationData'])
        data_fields = json.loads(df.loc[0, 'ApplicationDataFields'])

        self.app_settings_header = f"[{app}_Settings]"
        self.app_data_header = f"[{app}_Data]"

        for key, value in app_data.items():
            df[key] = value

        print(df[data_fields].to_string())

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
