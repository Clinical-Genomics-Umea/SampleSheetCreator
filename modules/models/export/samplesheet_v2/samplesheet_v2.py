import pandas as pd


class IlluminaSampleSheetV2:
    """
    A class to generate Illumina SampleSheet v2 format files.

    The SampleSheet v2 format includes several sections:
    - Header: Contains run parameters and metadata
    - Reads: Specifies read lengths
    - Sequencing: Contains custom primer settings
    - Applications: List of software tools

    """

    def __init__(self):

        # standalone sections
        self._header = {}
        self._reads = {}
        self._sequencing = {}

        # application sections
        self._applications = []

        # header fields
        self._header_fields = [
                        'RunName',
                        'RunDescription',
                        'FileFormatVersion',
                        'InstrumentPlatform',
                        'InstrumentType',
                        'Custom_FastqExtractionTool'
        ]
        self._read_fields = [
                        'Index1Cycles',
                        'Index2Cycles',
                        'Read1Cycles',
                        'Read2Cycles',
        ]

        self._sequencing_fields = [
                        'CustomIndex1Primer',
                        'CustomIndex2Primer',
                        'CustomRead1Primer',
                        'CustomRead2Primer',
                        'LibraryPrepKits',
        ]

    def set_header_field(self, key: str, value: str) -> None:
        if key in self._header_fields:
            self._header[key] = value

    def set_sequencing_field(self, key: str, value: str):
        if key in self._sequencing_fields:
            self._sequencing[key] = value

    def set_read_field(self, key: str, value: str) -> None:
        if key in self._read_fields:
            self._reads[key] = value

    def set_application(self, application_name: str, settings: dict, data: pd.DataFrame) -> None:
        application = {
            'ApplicationName': application_name,
            'Settings': settings,
            'Data': data
        }

        self._applications.append(application)

    def generate(self) -> str:

        rows = list()

        rows.append('[Header]')
        for key, value in self._header.items():
            rows.append(f'{key},{value}')
        rows.append('')

        rows.append('[Reads]')
        for key, value in self._reads.items():
            rows.append(f'{key},{value}')
        rows.append('')

        rows.append('[Sequencing]')
        for key, value in self._sequencing.items():
            rows.append(f'{key},{value}')

        for application in self._applications:

            application_name = application.get('ApplicationName')
            settings_name = f'{application_name}_Settings'
            data_name = f'{application_name}_Data'

            rows.append(f'[{settings_name}]')
            for key, value in application.get('Settings').items():
                rows.append(f'{key},{value}')
            rows.append('')

            rows.append(f'[{data_name}]')
            for row in application.get('Data').to_csv(index=False).splitlines():
                rows.append(row)
            rows.append('')


        return '\n'.join(rows)
