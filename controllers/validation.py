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
