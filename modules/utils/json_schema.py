import json
from pathlib import Path
from pprint import pprint


def infer_type(value):
    """Infer the JSON type from a Python value."""
    if isinstance(value, str):
        return "string"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, bool):
        return "boolean"
    elif value is None:
        return "null"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object"
    return "string"


def generate_schema(data):
    """Generate a JSON schema for a given JSON object."""
    if isinstance(data, list):
        # Assume homogeneous lists and analyze the first item
        if len(data) > 0:
            return {"type": "array", "items": generate_schema(data[0])}
        else:
            return {"type": "array", "items": {}}

    elif isinstance(data, dict):
        properties = {}
        required = []
        for key, value in data.items():
            properties[key] = generate_schema(value)
            required.append(key)
        return {"type": "object", "properties": properties, "required": required}

    else:
        return {"type": infer_type(data)}


if __name__ == "__main__":
    json_file_path = Path(
        "../../config/indexes/data/ILMN_DNA-RNA_UD_Indexes_SetD_Tagm_PCR-Free.json"
    )  # Path to your JSON file

    with open(json_file_path, "r") as f:
        json_data = json.load(f)

    schema = generate_schema(json_data)

    pprint(schema)

    # schema_file_path = "schema.json"
    # with open(schema_file_path, "w") as f:
    #     json.dump(schema, f, indent=4)
    #
    # print(f"JSON Schema saved to {schema_file_path}")
