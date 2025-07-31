from __future__ import annotations
from typing import Dict, Any, Optional, Union, List, TypeVar
import logging

import pandas as pd

# Type variable for DataFrame-like objects
DataFrameT = TypeVar('DataFrameT', bound=pd.DataFrame)


class IndexKit:
    """A class representing an index kit with associated metadata and index sets.
    
    This class encapsulates the data and functionality related to a specific index kit,
    including its name, adapter sequences, index lengths, and index sets.
    
    Args:
        index_kit_data: Dictionary containing the index kit configuration data.
        
    Raises:
        KeyError: If required fields are missing from index_kit_data.
        ValueError: If index lengths are invalid or data is malformed.
    """
    
    def __init__(self, index_kit_data: Dict[str, Any]) -> None:
        """Initialize the IndexKit with the provided configuration data."""
        self._logger = logging.getLogger(__name__)
        self._validate_index_kit_data(index_kit_data)
        
        # Initialize instance variables with type hints
        self.index_set: Dict[str, pd.DataFrame] = {}
        self._index_kit_name: str = index_kit_data["IndexKitName"]
        self._override_cycles_pattern: Optional[str] = index_kit_data.get("OverrideCyclesPattern")
        
        # Handle adapters
        adapters = index_kit_data.get("Adapters", {})
        self._adapter_read_1: Optional[str] = adapters.get("AdapterRead1")
        self._adapter_read_2: Optional[str] = adapters.get("AdapterRead2")
        
        # Handle index lengths with validation
        self._index_i7_len: int = int(index_kit_data.get("IndexI7Len", 0))
        self._index_i5_len: int = int(index_kit_data.get("IndexI5Len", 0))
        
        self._initialize_index_sets(index_kit_data.get('IndexSets', {}))
    
    def _validate_index_kit_data(self, data: Dict[str, Any]) -> None:
        """Validate the structure and content of the index kit data.
        
        Args:
            data: The index kit data to validate.
            
        Raises:
            KeyError: If required fields are missing.
            ValueError: If data format is invalid.
        """
        required_fields = ["IndexKitName", "Adapters", "IndexI7Len", "IndexI5Len"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"Missing required field: {field}")
        
        if not isinstance(data.get("Adapters"), dict):
            raise ValueError("Adapters must be a dictionary")
            
        if not isinstance(data.get("IndexI7Len"), (int, float)) or not isinstance(data.get("IndexI5Len"), (int, float)):
            raise ValueError("Index lengths must be numbers")
    
    def _initialize_index_sets(self, index_sets: Dict[str, Any]) -> None:
        """Initialize the index sets from the provided data.
        
        Args:
            index_sets: Dictionary containing index set data.
        """
        for name, index_data in index_sets.items():
            try:
                if not index_data:  # Skip empty index sets
                    self._logger.warning(f"Empty index set found: {name}")
                    continue
                    
                # Convert index data to DataFrame
                df = pd.DataFrame.from_dict(index_data)
                
                # Add metadata columns
                df["IndexKitName"] = self._index_kit_name
                if self._adapter_read_1 is not None:
                    df["AdapterRead1"] = self._adapter_read_1
                if self._adapter_read_2 is not None:
                    df["AdapterRead2"] = self._adapter_read_2
                if self._override_cycles_pattern is not None:
                    df["OverrideCyclesPattern"] = self._override_cycles_pattern
                
                self.index_set[name] = df
                
            except Exception as e:
                self._logger.error(f"Error initializing index set '{name}': {e}")
                continue
    
    @property
    def name(self) -> str:
        """Get the name of the index kit.
        
        Returns:
            The name of the index kit.
        """
        return self._index_kit_name
    
    @property
    def index_i7_len(self) -> int:
        """Get the length of the i7 index.
        
        Returns:
            The length of the i7 index in bases.
        """
        return self._index_i7_len
    
    @property
    def index_i5_len(self) -> int:
        """Get the length of the i5 index.
        
        Returns:
            The length of the i5 index in bases.
        """
        return self._index_i5_len
    
    def get_index_set(self, name: str) -> Optional[pd.DataFrame]:
        """Get an index set by name.
        
        Args:
            name: The name of the index set to retrieve.
            
        Returns:
            The requested index set as a DataFrame, or None if not found.
        """
        return self.index_set.get(name)
    
    def get_all_index_sequences(self) -> Dict[str, List[str]]:
        """Get all index sequences from all index sets.
        
        Returns:
            A dictionary mapping index set names to lists of index sequences.
        """
        result = {}
        for name, df in self.index_set.items():
            # Assuming the sequence column is named 'sequence' or similar
            # Adjust the column name based on your actual data structure
            if not df.empty and 'sequence' in df.columns:
                result[name] = df['sequence'].tolist()
        return result
    
    def validate_index_sequence(self, sequence: str, index_type: str = 'i7') -> bool:
        """Validate if a sequence matches the expected length for its index type.
        
        Args:
            sequence: The index sequence to validate.
            index_type: The type of index ('i7' or 'i5').
            
        Returns:
            bool: True if the sequence is valid, False otherwise.
            
        Raises:
            ValueError: If an invalid index_type is provided.
        """
        if not isinstance(sequence, str):
            return False
            
        if index_type.lower() == 'i7':
            return len(sequence) == self._index_i7_len
        elif index_type.lower() == 'i5':
            return len(sequence) == self._index_i5_len
        else:
            raise ValueError(f"Invalid index type: {index_type}. Must be 'i7' or 'i5'.")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the IndexKit instance to a dictionary.
        
        Returns:
            A dictionary representation of the IndexKit.
        """
        index_sets = {}
        for name, df in self.index_set.items():
            # Convert DataFrame back to dict format
            index_sets[name] = df.to_dict('records')
        
        return {
            "IndexKitName": self._index_kit_name,
            "OverrideCyclesPattern": self._override_cycles_pattern,
            "Adapters": {
                "AdapterRead1": self._adapter_read_1,
                "AdapterRead2": self._adapter_read_2
            },
            "IndexI7Len": self._index_i7_len,
            "IndexI5Len": self._index_i5_len,
            "IndexSets": index_sets
        }
    
    def __repr__(self) -> str:
        """Return a string representation of the IndexKit."""
        return (f"<IndexKit(name='{self._index_kit_name}', "
                f"i7_len={self._index_i7_len}, i5_len={self._index_i5_len}, "
                f"index_sets={len(self.index_set)})>")
