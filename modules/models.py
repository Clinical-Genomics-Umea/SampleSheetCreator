import json


def read_fields_from_json(json_file_path):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            fields = data.get("fields", [])
            return fields
    except FileNotFoundError:
        print("JSON file not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return []


