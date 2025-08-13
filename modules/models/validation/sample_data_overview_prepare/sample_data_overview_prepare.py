from typing import Tuple, Optional, Any
import logging
from logging import Logger
import pandas as pd
from PySide6.QtCore import Signal, QObject

from modules.models.state.state_model import StateModel


class SampleDataOverviewPrepare(QObject):
    """Prepares sample data for display in the overview widget by exploding application profiles and lanes.
    
    This class takes a pandas DataFrame from the state model and creates multiple views of the data:
    - Original data
    - Data with exploded application profiles
    - Data with exploded lanes
    
    Signals:
        data_ready: Emitted when data preparation is complete. Emits a tuple of DataFrames.
    """
    
    data_ready = Signal(tuple)  # (original_df, app_exploded_df, lane_exploded_df)

    def __init__(self, state_model: StateModel, logger: Optional[Logger] = None) -> None:
        """Initialize the data preparer.
        
        Args:
            state_model: The application state model containing the sample data
            logger: Optional logger instance. If not provided, a default logger will be created.
        """
        super().__init__()
        
        self._logger = logger or logging.getLogger(__name__)
        
        if not state_model:
            raise ValueError("state_model cannot be None")
            
        if not hasattr(state_model, 'sample_df') or state_model.sample_df is None:
            self._logger.warning("No sample data available in state model")
            
        self._state_model = state_model

    @staticmethod
    def _appname_explode(df: pd.DataFrame) -> pd.DataFrame:
        """Explode the ApplicationProfile column into separate rows.
        
        Args:
            df: Input DataFrame with ApplicationProfile column
            
        Returns:
            DataFrame with ApplicationProfile values exploded into separate rows
        """
        if df.empty or 'ApplicationProfile' not in df.columns:
            return df.copy()
            
        # Filter out empty application profiles and explode
        filtered = df[df["ApplicationProfile"].apply(lambda x: bool(x))].copy()
        return filtered.explode("ApplicationProfile", ignore_index=True) if not filtered.empty else filtered

    @staticmethod
    def _lane_explode(df: pd.DataFrame) -> pd.DataFrame:
        """Explode the Lane column into separate rows.
        
        Args:
            df: Input DataFrame with Lane column
            
        Returns:
            DataFrame with Lane values exploded into separate rows
        """
        if df.empty or 'Lane' not in df.columns:
            return df.copy()
            
        # Filter out empty lanes and explode
        filtered = df[df["Lane"].apply(lambda x: bool(x))].copy()
        return filtered.explode("Lane", ignore_index=True) if not filtered.empty else filtered

    def data_to_data_widget(self) -> None:
        """Prepare and emit the data for the overview widget.
        
        Processes the sample data and emits a tuple containing:
        - Original DataFrame
        - DataFrame with exploded application profiles
        - DataFrame with exploded lanes
        """
        if not hasattr(self._state_model, 'sample_df') or self._state_model.sample_df is None:
            self._logger.error("No sample data available"
                             " in state model")
            return
            
        try:
            sample_df = self._state_model.sample_df
            
            # Ensure we're working with a copy to avoid modifying the original
            df = sample_df.copy()
            
            # Create the different views
            app_exploded = self._appname_explode(df)
            lane_exploded = self._lane_explode(df)
            
            # Emit the prepared data
            self.data_ready.emit((df, app_exploded, lane_exploded))
            
        except Exception as e:
            self._logger.exception("Error preparing data for overview widget")
            # Emit empty DataFrames with the same structure on error
            self.data_ready.emit((pd.DataFrame(), pd.DataFrame(), pd.DataFrame()))

