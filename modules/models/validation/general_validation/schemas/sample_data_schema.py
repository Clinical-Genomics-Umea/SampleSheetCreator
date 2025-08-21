from pydantic import BaseModel, field_validator, model_validator, Optional
import pandas as pd


class BaseSampleDataSchema(BaseModel):
    Lane: list[int]
    Sample_ID: str
    Pos: Optional[str]
    IndexI7Name: Optional[str]
    IndexI7: str
    IndexI5Name: Optional[str]
    IndexI5: Optional[str]
    IndexKitName: Optional[str]
    OverrideCyclesPattern: Optional[str]
    BarcodeMismatchesIndex1: Optional[str]
    BarcodeMismatchesIndex2: Optional[str]
    AdapterRead1: Optional[str]
    AdapterRead2: Optional[str]
    ApplicationProfile: list[str]

    @field_validator('Lane', 'Sample_ID', 'IndexI7', 'ApplicationProfile')
    def no_missing_values(cls, v, info):
        if any(pd.isna(v)):
            raise ValueError(f"Missing values detected in required column '{info.field_name}'")
        return v

    @model_validator(mode='after')
    def check_sample_id_uniqueness(self):
        if len(self.Sample_ID) != len(set(self.Sample_ID)):
            duplicates = pd.Series(self.Sample_ID).value_counts()
            duplicates = duplicates[duplicates > 1].index.tolist()
            raise ValueError(f"Duplicate Sample_IDs found: {duplicates}")
        return self

