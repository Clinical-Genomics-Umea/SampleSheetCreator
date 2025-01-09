from pprint import pprint

import pandas as pd

from utils.utils import reverse_complement

tr = {"bcl2fastq": "BCL2Fastq", "bclconvert": "BCLConvert"}


def samplesheet_v2(data_obj, fastq_extraction_tool):

    fastq_extraction_tool = tr[fastq_extraction_tool]

    i5_samplesheet_orientation = data_obj["SampleSheetConfig"][
        "I5SampleSheetOrientation"
    ][fastq_extraction_tool]

    header = ["[Header]"]
    for k, v in data_obj["Header"].items():
        header.append(f"{k},{v}")

    header.append(f"Custom_FastqExtractionTool, {fastq_extraction_tool}")

    reads = ["[Reads]"]
    for k, v in data_obj["Reads"].items():
        reads.append(f"{k},{v}")

    applications = []
    for app_obj in data_obj["Applications"]:

        app = app_obj["Application"]

        if app_obj["ApplicationGroupName"] == "dragen":
            applications.append(f"[{app}_Settings]")

            for k, v in app_obj["Settings"].items():
                applications.append(f"{k},{v}")

            applications.append("")

            applications.append(f"[{app}_Data]")

            data_df = pd.DataFrame.from_dict(app_obj["Data"])

            if i5_samplesheet_orientation == "rc" and "IndexI5" in data_df.columns:
                data_df["IndexI5"] = data_df["IndexI5"].apply(reverse_complement)

            data_df.rename(
                {"IndexI7": "Index", "IndexI5": "Index2"}, inplace=True, axis="columns"
            )

            csv_obj = data_df.to_csv(index=False).splitlines()
            applications.extend(csv_obj)
            applications.append("")

    output = header
    output.append("")
    output.extend(reads)
    output.append("")
    output.extend(applications)

    return "\n".join(output)
