import csv
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path


class IlluminaSampleSheetV1:
    """
    A class to generate Illumina SampleSheet v1 format files.

    The SampleSheet v1 format includes several sections:
    - Header: Contains run parameters and metadata
    - Reads: Specifies read lengths
    - Settings: Contains bcl2fastq settings
    - Data: Sample information and demultiplexing data
    """

    def __init__(self):
        self.header = {}
        self.reads = []
        self.settings = {}
        self.data = []
        self._setup_defaults()

    def _setup_defaults(self):
        """Set up default values for common fields."""
        self.header = {
            'IEMFileVersion': '4',
            'Investigator Name': '',
            'Experiment Name': '',
            'Date': datetime.now().strftime('%m/%d/%Y'),
            'Workflow': 'GenerateFASTQ',
            'Application': 'FASTQ Only',
            'Assay': 'TruSeq HT',
            'Description': '',
            'Chemistry': 'Default'
        }

        self.settings = {
            'ReverseComplement': '0',
            'Adapter': 'AGATCGGAAGAGCACACGTCTGAACTCCAGTCA',
            'AdapterRead2': 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT'
        }

    def set_header_field(self, key: str, value: str) -> None:
        """Set a header field."""
        self.header[key] = value

    def set_experiment_info(self, investigator_name: str, experiment_name: str,
                            description: str = '', assay: str = 'TruSeq HT') -> None:
        """Set basic experiment information."""
        self.header['Investigator Name'] = investigator_name
        self.header['Experiment Name'] = experiment_name
        self.header['Description'] = description
        self.header['Assay'] = assay

    def add_read(self, num_cycles: int) -> None:
        """Add a read configuration."""
        self.reads.append(num_cycles)

    def set_setting(self, key: str, value: str) -> None:
        """Set a bcl2fastq setting."""
        self.settings[key] = value

    def add_sample(self, sample_id: str, sample_name: str, sample_plate: str = '',
                   sample_well: str = '', i7_index_id: str = '', index: str = '',
                   i5_index_id: str = '', index2: str = '', sample_project: str = '',
                   description: str = '', **kwargs) -> None:
        """
        Add a sample to the Data section.

        Args:
            sample_id: Unique sample identifier
            sample_name: Sample name
            sample_plate: Sample plate identifier
            sample_well: Well position (e.g., A01)
            i7_index_id: I7 index identifier/name
            index: I7 index sequence
            i5_index_id: I5 index identifier/name
            index2: I5 index sequence
            sample_project: Project name
            description: Sample description
            **kwargs: Additional custom fields
        """
        sample_data = {
            'Sample_ID': sample_id,
            'Sample_Name': sample_name,
            'Sample_Plate': sample_plate,
            'Sample_Well': sample_well,
            'I7_Index_ID': i7_index_id,
            'index': index,
            'I5_Index_ID': i5_index_id,
            'index2': index2,
            'Sample_Project': sample_project,
            'Description': description
        }

        # Add any additional custom fields
        sample_data.update(kwargs)

        self.data.append(sample_data)

    def add_samples_from_list(self, samples: List[Dict]) -> None:
        """
        Add multiple samples from a list of dictionaries.

        Args:
            samples: List of sample dictionaries with required fields
        """
        for sample in samples:
            self.add_sample(**sample)

    def set_paired_end_reads(self, read1_cycles: int, read2_cycles: int) -> None:
        """
        Set up paired-end sequencing reads.

        Args:
            read1_cycles: Number of cycles for Read 1
            read2_cycles: Number of cycles for Read 2
        """
        self.reads = [read1_cycles, read2_cycles]

    def set_single_end_reads(self, read1_cycles: int) -> None:
        """
        Set up single-end sequencing reads.

        Args:
            read1_cycles: Number of cycles for Read 1
        """
        self.reads = [read1_cycles]

    def set_standard_adapters(self, truseq: bool = True) -> None:
        """
        Set standard Illumina adapter sequences.

        Args:
            truseq: If True, use TruSeq adapters; if False, use Nextera adapters
        """
        if truseq:
            self.settings['Adapter'] = 'AGATCGGAAGAGCACACGTCTGAACTCCAGTCA'
            self.settings['AdapterRead2'] = 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT'
        else:
            # Nextera adapters
            self.settings['Adapter'] = 'CTGTCTCTTATACACATCT'
            self.settings['AdapterRead2'] = 'CTGTCTCTTATACACATCT'

    def generate_samplesheet(self) -> str:
        """Generate the complete samplesheet as a string."""
        lines = []

        # Header section
        lines.append('[Header]')
        for key, value in self.header.items():
            lines.append(f'{key},{value}')
        lines.append('')

        # Reads section
        if self.reads:
            lines.append('[Reads]')
            for read_cycles in self.reads:
                lines.append(str(read_cycles))
            lines.append('')

        # Settings section
        if self.settings:
            lines.append('[Settings]')
            for key, value in self.settings.items():
                lines.append(f'{key},{value}')
            lines.append('')

        # Data section
        if self.data:
            lines.append('[Data]')

            # Get all unique column names from all samples
            all_columns = set()
            for sample in self.data:
                all_columns.update(sample.keys())

            # Standard column order for v1
            standard_cols = [
                'Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
                'I7_Index_ID', 'index', 'I5_Index_ID', 'index2',
                'Sample_Project', 'Description'
            ]

            ordered_cols = []

            # Add standard columns first if they exist
            for col in standard_cols:
                if col in all_columns:
                    ordered_cols.append(col)
                    all_columns.remove(col)

            # Add any remaining columns
            ordered_cols.extend(sorted(all_columns))

            # Write header
            lines.append(','.join(ordered_cols))

            # Write sample data
            for sample in self.data:
                row_values = []
                for col in ordered_cols:
                    value = sample.get(col, '')
                    # Handle values that might contain commas
                    if ',' in str(value):
                        value = f'"{value}"'
                    row_values.append(str(value))
                lines.append(','.join(row_values))

        return '\n'.join(lines)

    def save_samplesheet(self, filename: Union[str, Path]) -> None:
        """Save the samplesheet to a file."""
        content = self.generate_samplesheet()
        with open(filename, 'w', newline='') as f:
            f.write(content)

    def validate_samples(self) -> List[str]:
        """
        Basic validation of sample data.

        Returns:
            List of validation error messages
        """
        errors = []

        if not self.data:
            errors.append("No samples defined")
            return errors

        sample_ids = []
        for i, sample in enumerate(self.data):
            row_num = i + 1

            # Check required fields
            if not sample.get('Sample_ID'):
                errors.append(f"Row {row_num}: Sample_ID is required")
            else:
                sample_ids.append(sample['Sample_ID'])

            if not sample.get('Sample_Name'):
                errors.append(f"Row {row_num}: Sample_Name is required")

            # Check index sequences if provided
            index = sample.get('index', '')
            index2 = sample.get('index2', '')

            if index and not all(c in 'ACGT' for c in index.upper()):
                errors.append(f"Row {row_num}: index contains invalid characters (should be ACGT)")

            if index2 and not all(c in 'ACGT' for c in index2.upper()):
                errors.append(f"Row {row_num}: index2 contains invalid characters (should be ACGT)")

        # Check for duplicate sample IDs
        duplicate_ids = set([x for x in sample_ids if sample_ids.count(x) > 1])
        if duplicate_ids:
            errors.append(f"Duplicate Sample_IDs found: {', '.join(duplicate_ids)}")

        return errors

    def add_manifests_section(self, manifests: List[str]) -> None:
        """
        Add a Manifests section (used for targeted sequencing).

        Args:
            manifests: List of manifest file paths
        """
        self.manifests = manifests

    def generate_samplesheet_with_manifests(self) -> str:
        """Generate samplesheet including Manifests section if present."""
        content = self.generate_samplesheet()

        if hasattr(self, 'manifests') and self.manifests:
            lines = content.split('\n')
            # Insert manifests section before Data section
            data_index = -1
            for i, line in enumerate(lines):
                if line == '[Data]':
                    data_index = i
                    break

            if data_index >= 0:
                manifest_lines = ['[Manifests]']
                for manifest in self.manifests:
                    manifest_lines.append(manifest)
                manifest_lines.append('')

                lines = lines[:data_index] + manifest_lines + lines[data_index:]
                content = '\n'.join(lines)

        return content


# Predefined index sets for common Illumina kits
class IlluminaIndexSets:
    """Common Illumina index sequences for different kits."""

    # TruSeq HT (96 samples) - subset shown
    TRUSEQ_HT_I7 = {
        'N701': 'TAAGGCGA', 'N702': 'CGTACTAG', 'N703': 'AGGCAGAA', 'N704': 'TCCTGAGC',
        'N705': 'GGACTCCT', 'N706': 'TAGGCATG', 'N707': 'CTCTCTAC', 'N708': 'CAGAGAGG',
        'N709': 'GCTACGCT', 'N710': 'CGAGGCTG', 'N711': 'AAGAGGCA', 'N712': 'GTAGAGGA'
    }

    TRUSEQ_HT_I5 = {
        'S501': 'TAGATCGC', 'S502': 'CTCTCTAT', 'S503': 'TATCCTCT', 'S504': 'AGAGTAGA',
        'S505': 'GTAAGGAG', 'S506': 'ACTGCATA', 'S507': 'AAGGAGTA', 'S508': 'CTAAGCCT'
    }

    # Nextera XT v2 (96 samples) - subset shown
    NEXTERA_XT_I7 = {
        'N701': 'TCGCCTTA', 'N702': 'CTAGTACG', 'N703': 'TTCTGCCT', 'N704': 'GCTCAGGA',
        'N705': 'AGGAGTCC', 'N706': 'CATGCCTA', 'N707': 'GTAGAGAG', 'N708': 'CCTCTCTG'
    }

    NEXTERA_XT_I5 = {
        'S501': 'GCGATAGA', 'S502': 'ATAGAGAG', 'S503': 'AGAGGATA', 'S504': 'TCTACTCT',
        'S505': 'CTCCTTAC', 'S506': 'TATGCAGT', 'S507': 'TACTCCTT', 'S508': 'AGGCTAAG'
    }
