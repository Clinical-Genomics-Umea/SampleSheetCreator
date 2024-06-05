from dataclasses import dataclass
import pandas as pd
import pandera as pa
import json


class SampleSheetV2:
    def __init__(self, run_info: dict, sample_df: pd.DataFrame):

        if sample_df.empty:
            return

        r1, i1, i2, r2 = run_info['Reads']['ReadProfile'].strip().split('-')
        self.run_cycles = dict()
        self.run_cycles['read1'] = int(r1)
        self.run_cycles['index'] = int(i1)
        self.run_cycles['index2'] = int(i2)
        self.run_cycles['read2'] = int(r2)

        self.standalones = dict()

        self.standalones['Header'] = Header(run_info)
        self.standalones['Reads'] = Reads(run_info)

        self.applications = []

        sample_df_override = self.add_override_cycles(sample_df)

        self.applications.append(BCLConvert(sample_df_override))

        used_applications = sample_df_override['Application'].unique()
        for app in used_applications:
            df_subset = sample_df_override[sample_df_override['Application'] == app]
            self.applications.append(Application(df_subset))

        for app in self.applications:
            ss = app.samplesheet_list()

            for line in ss:
                print(line)

    def add_override_cycles(self, df):
        df['OverrideCycles'] = df.apply(lambda row: self.get_override_cycles(row['Index_I7'], row['Index_I5']), axis=1)
        return df

    def get_override_cycles(self, index, index2):
        len_index = len(str(index))
        len_index2 = len(str(index2))

        read1 = f"Y{self.run_cycles['read1']}"
        read2 = f"Y{self.run_cycles['read2']}"

        i_index1, n_index1 = len_index, self.run_cycles['index'] - len_index
        i_index2, n_index2 = len_index2, self.run_cycles['index2'] - len_index2
        index1 = f"{i_index1}N{n_index1}" if n_index1 > 0 else f"I{i_index1}"
        index2 = f"N{n_index2}I{i_index2}" if n_index2 > 0 else f"I{i_index2}"

        return f"{read1};{index1};{index2};{read2}"


class Header:
    def __init__(self, run_info):
        self.header = "[Header]"
        self.data = {}

        self.set_data(run_info)

    def set_data(self, run_info):
        self.data = {
            'FileFormatVersion': run_info['Header']['FileFormatVersion'],
            'RunName': run_info['Header']['RunName'],
            'RunDescription': run_info['Header']['RunName'],
            'InstrumentPlatform': self.get_platform(run_info['Header']['Instrument']),
            'InstrumentType': run_info['Header']['Instrument']
        }

    @staticmethod
    def get_platform(instrument):
        instrument_to_platform = {
            'NextSeq1000': 'NextSeq1000',
            'NextSeq2000': 'NextSeq2000',
            'NovaSeqX': 'NovaSeqXSeries'
        }

        return instrument_to_platform[instrument]


class Reads:
    def __init__(self, run_info: dict):
        self.header = "[Reads]"
        self.data = {}

    def set_data(self, run_info: dict):
        r1, i1, i2, r2 = run_info['Reads']['ReadProfile'].strip().split('-')

        self.data = {
            'Read1Cycles': r1,
            'Read2Cycles': r2,
            'Index1Cycles': i1,
            'Index2Cycles': i2,
        }

@dataclass
class Sequencing:
    CustomIndex1Primer: str
    CustomIndex2Primer: str
    CustomRead1Primer: str
    CustomRead2Primer: str
    LibraryPrepKits: str


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
                       "index",
                       "index2",
                       "AdapterRead1",
                       "AdapterRead2",
                       "BarcodeMismatchesIndex1",
                       "BarcodeMismatchesIndex2",
                       "OverrideCycles"
                       ]

        df.rename(columns={'Index_I7': 'index', 'Index_I5': 'index2'}, inplace=True)
        self.data = df[data_fields]

    def samplesheet_list(self):

        output = list()

        output.append(self.app_settings_header)
        for key, value in self.app_settings.items():
            output.append(f"{key},{value}")

        output.append("")
        output.append(self.app_data_header)
        output.extend(self.data.to_csv(sep=',', index=False).split("\n"))

        return output

    class Application:
        def __init__(self, df):

            app = df.loc[0, 'Application']
            self.app_settings = json.loads(df.loc[0, 'ApplicationSettings'])
            app_data = json.loads(df.loc[0, 'ApplicationData'])
            data_fields = json.loads(df.loc[0, 'ApplicationDataFields'])

            self.app_settings_header = f"[{app}_Settings]"
            self.app_data_header = f"[{app}_Data]"

            for key, value in app_data:
                df[key] = value

            self.data = df[data_fields]

        def samplesheet_list(self):

            output = list()

            output.append(self.app_settings_header)
            for key, value in self.app_settings.items():
                output.append(f"{key}={value}")

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

        print(app_data)

        self.app_settings_header = f"[{app}_Settings]"
        self.app_data_header = f"[{app}_Data]"

        for key, value in app_data.items():
            df[key] = value

        print(df[data_fields].to_string())

        self.data = self.reorder_columns(df[data_fields],"Sample_ID")

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


    def samplesheet_list(self):

        output = list()

        output.append(self.app_settings_header)
        for key, value in self.app_settings.items():
            output.append(f"{key}={value}")

        output.append("")
        output.append(self.app_data_header)
        output.extend(self.data.to_csv(sep=',', index=False).split("\n"))

        return output


class DragenGermline:
    def __init__(self, df):
        self.settings_header = "[DragenGermline_Settings]"
        self.data_header = "[DragenGermline_Data]"

        app_profile_list = df['AppProfile'].unique()
        app_profile = json.loads(app_profile_list[0])

        self.settings = app_profile['Settings']
        self.data = pd.DataFrame()

        for key, value in app_profile['Data'].items():
            df[key] = value

        self.fields = ["ReferenceGenomeDir",
                       "VariantCallingMode",
                       "QcCoverage1BedFile",
                       "QcCoverage2BedFile",
                       "QcCoverage3BedFile",
                       "QcCrossContaminationVcfFile",
                       "Sample_ID"]

        self.data = df[self.fields]

        print(self.data.to_string())


class DragenEnrichment:
    def __init__(self, df):
        self.settings_header = "[DragenEnrichment_Settings]"
        self.data_header = "[DragenEnrichment_Data]"

        self.settings = {}
        self.data = pd.DataFrame()

        self.data_fields = ["ReferenceGenomeDir",
                            "Bedfile",
                            "GermlineOrSomatic",
                            "AuxNoiseBaselineFile"
                            "AuxCnvPanelOfNormalsFile"
                            "QcCoverage1BedFile",
                            "VariantCallingMode",
                            "Sample_ID"]





class DragenRNA:
    def __init__(self, dragen_germline_settings, dragen_germline_data):

        self.settings_header = "[DragenRNA_Settings]"
        self.data_header = "[DragenRNA_Data]"

        self.settings = {
            'SoftwareVersion': "",
            'AppVersion': "",
            'KeepFastQ': True,
            'MapAlignOutFormat': "bam",
            'DifferentialExpressionEnable': ""
        }

        self.data = pd.DataFrame(columns=["ReferenceGenomeDir",
                                          "RnaGeneAnnotationFile",
                                          "RnaPipelineMode",
                                          "DownSampleNumReads",
                                          "Sample_ID",
                                          "Comparison1"
                                          "Comparison2"
                                          "Comparison3",
                                          "Comparison4",
                                          "Comparison5"])


class DragenSomatic:
    def __init__(self, dragen_germline_settings, dragen_germline_data):

        self.settings_header = "[DragenSomatic_Settings]"
        self.data_header = "[DragenSomatic_Data]"

        self.settings = {
            'SoftwareVersion': "",
            'AppVersion': "",
            'KeepFastQ': True,
            'MapAlignOutFormat': "bam",
        }

        self.data = pd.DataFrame(columns=["ReferenceGenomeDir",
                                          "Bedfile",
                                          "AuxNoiseBaselineFile",
                                          "AuxSvNoiseBaselineFile",
                                          "AuxCnvPopBAlleleVcfFile",
                                          "AuxGermlineTaggingFile",
                                          "QcCoverage1BedFile",
                                          "VariantCallingMode",
                                          "Sample_ID"])


class DragenMethylation:
    def __init__(self, dragen_germline_settings, dragen_germline_data):

        self.settings_header = "[DragenMethylation_Settings]"
        self.data_header = "[DragenMethylation_Data]"

        self.settings = {
            'SoftwareVersion': "",
            'AppVersion': "",
            'KeepFastQ': True,
            'MapAlignOutFormat': "bam",
            'UsesTaps': ""
        }

        self.data = pd.DataFrame(columns=["ReferenceGenomeDir",
                                          "MethylationProtocol",
                                          "Sample_ID"])

