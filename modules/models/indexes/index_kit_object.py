
import pandas as pd


class IndexKitObject:

    def __init__(self, index_kit_data):
        self.index_set = {}
        self._index_kit_name = index_kit_data["IndexKitName"]
        self._override_cycles_pattern = index_kit_data["OverrideCyclesPattern"] or None
        self._adapter_read_1 = index_kit_data["Adapters"]["AdapterRead1"] or None
        self._adapter_read_2 = index_kit_data["Adapters"]["AdapterRead2"] or None
        self._index_i7_len = index_kit_data["IndexI7Len"] or 0
        self._index_i5_len = index_kit_data["IndexI5Len"] or 0

        for name in index_kit_data['IndexSets']:
            self.index_set[name] = pd.DataFrame.from_dict(
                index_kit_data["IndexSets"][name]
            )
            self.index_set[name]["IndexKitName"] = self._index_kit_name
            self.index_set[name]["AdapterRead1"] = self._adapter_read_1
            self.index_set[name]["AdapterRead2"] = self._adapter_read_2
            self.index_set[name]["OverrideCyclesPattern"] = self._override_cycles_pattern

    @property
    def name(self):
        return self._index_kit_name

    @property
    def index_i7_len(self):
        return self._index_i7_len

    @property
    def index_i5_len(self):
        return self._index_i5_len
