import json

import pandas as pd


def to_samplesheetv2(sample_obj):


    output = ["[Header]"]

    for k, v in sample_obj["Header"].items():
        output.append(f"{k},{v}")

    output.append("")

    output.append("[Reads]")
    for k, v in sample_obj["Reads"].items():
        output.append(f"{k},{v}")

    output.append("")

    for app_obj in sample_obj["Applications"]:
        app = app_obj["Application"]
        output.append(f"[{app}_Settings]")

        for k, v in app_obj["Settings"].items():
            output.append(f"{k},{v}")

        output.append("")

        df = pd.DataFrame.from_dict(app_obj["Data"])
        csv_list = df.to_csv(index=False).splitlines()

        output.append(f"[{app}_Data]")
        output.extend(csv_list)

        output.append("")

    return "\n".join(output)


def to_json(sample_obj):
    return json.dumps(sample_obj)
