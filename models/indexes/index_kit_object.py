from pprint import pprint

import pandas as pd


class IndexKitObject:

    def __init__(self, index_kit_data):
        pprint(index_kit_data)

        self._name = index_kit_data["Name"]
        self._supported_library_prep_kits = index_kit_data["SupportedLibraryKits"]
        self._index_set_names = index_kit_data["UsedIndexSets"]

        self.index_sets = {}

        for name in self._index_set_names:
            self.index_sets[name] = pd.DataFrame.from_dict(
                index_kit_data["IndexSets"][name]
            )

        self._override_cycles_pattern = index_kit_data["OverrideCyclesPattern"] or None

        self._adapter_read_1 = index_kit_data["Adapters"]["AdapterRead1"] or None
        self._adapter_read_2 = index_kit_data["Adapters"]["AdapterRead2"] or None

    @property
    def name(self):
        return self._name

    @property
    def i7_len(self):
        return self._supported_library_prep_kits
