import re
from logging import Logger

from PySide6.QtCore import Signal, QObject, Slot
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.datastate.datastate_model import DataStateModel
from modules.models.state.state_model import StateModel


class OverrideCyclesModel(QObject):
    override_cycles_ok = Signal(object)

    def __init__(self,
                 state_model: StateModel,
                 dataset_manager: DataSetManager,
                 logger: Logger):
        super().__init__()
        self._logger = logger
        self._dataset_manager = dataset_manager
        self._state_model = state_model

        self._oc_validate_pattern = {
            "Read1Cycles": r"^(Y\d+|N\d+|U\d+)*(Y{r})(Y\d+|N\d+|U\d+)*$",
            "Index1Cycles": r"^(I\d+|N\d+|U\d+)*(I{i})(I\d+|N\d+|U\d+)*$",
            "Index2Cycles": r"^(I\d+|N\d+|U\d+)*(I{i})(I\d+|N\d+|U\d+)*$",
            "Read2Cycles": r"^(Y\d+|N\d+|U\d+)*(Y{r})(Y\d+|N\d+|U\d+)*$",
        }

        self._oc_parts_re = {
            "Read1Cycles": r"(Y\d+|N\d+|U\d+|Y{r})",
            "Index1Cycles": r"(I\d+|N\d+|U\d+|I{i})",
            "Index2Cycles": r"(I\d+|N\d+|U\d+|I{i})",
            "Read2Cycles": r"(Y\d+|N\d+|U\d+|Y{r})",
        }

        self._digits_re = re.compile(r'^\d+')
        self._left_nondigits_re = re.compile(r'^\D+')
        self._placeholder_re = re.compile(r'\{[ir]\}')

    def override_cycles_validate(self, override_cycles_dict: dict) -> bool:

       for key, value in override_cycles_dict.items():
           if not self._validate_override_pattern(key, override_cycles_dict[key]):
               self._logger.error(f"override cycles validation failed for {key} : {value}")
               return False

           if not self._validate_override_len(key, override_cycles_dict[key]):
               self._logger.error(f"override cycles length validation failed for {key} : {value}")
               return False

       return True

    def override_cycles_dict_to_str(self, override_cycles_dict: dict) -> str:
        """
        Take a dictionary of override cycles and convert it to a string.
        """
        override_cycles_list = []

        for key in self._oc_validate_pattern:
            override_cycles_list.append(override_cycles_dict[key])

        return "-".join(override_cycles_list)


    def _validate_override_pattern(self, oc_part_key, oc_part_string):
        if re.fullmatch(self._oc_validate_pattern[oc_part_key], oc_part_string):
            return True

        self._logger.error("override cycles pattern validation failed for : " + oc_part_key)

        return False

    def _validate_override_len(self, oc_part_key, oc_part_string):
        nonvariable_oc_len = self._nonvariable_oc_len(oc_part_key, oc_part_string)

        if self._dataset_manager.read_cycles_dict[oc_part_key] < nonvariable_oc_len:
            self._logger.error("override cycles len validation failed for : " + oc_part_key)

        return True

    def _nonvariable_oc_len(self, oc_part_key, oc_part_str):
        matches = re.findall(self._oc_parts_re[oc_part_key], oc_part_str)

        preset_oc_len = 0
        for m in matches:
            if self._placeholder_re.search(m):
                continue

            preset_oc_len += int(m[1:])

        return preset_oc_len