from pathlib import Path

import numpy as np
import pandas as pd
import pandera as pa
from PySide6.QtCore import QObject, Signal

from models.configuration import ConfigurationManager
from models.validation_fns import padded_index_df
from models.pa_schema import prevalidation_schema
from models.samplesheet_model import SampleSheetModel
from views.run_setup_views import RunView
import yaml


def load_from_yaml(config_file):

    with open(config_file, "r") as file:
        return yaml.safe_load(file)


# def flowcell_validation(flowcell, instrument, settings):
#     if instrument not in settings["flowcells"]:
#         return (
#             False,
#             f"Instrument '{instrument}' not present in validation_settings.yaml .",
#         )
#     if flowcell not in settings["flowcells"][instrument]["type"]:
#         return False, f"flowcell '{flowcell}' not present in validation_settings.yaml ."
#
#     return True, ""
