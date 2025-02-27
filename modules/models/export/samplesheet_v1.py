import pandas as pd

samplesheet_v1_template = {
    "Header": {
        "Application": "FASTQ Only",
        "Investigator": "Investigator",
        "RunName": "RunName",
        "RunDescription": "RunDescription",
        "Flowcell": "Flowcell",
        "ReagentKit": "ReagentKit",
        "Date": "Date",
        "InstrumentType": "Instrument",
        "UUID7": "UUID7",
        "SampleSheetVersion": "SampleSheetVersion",
        "FastqExtractTool": "FastqExtractTool",
        "I5SampleSheetOrientation": "I5SampleSheetOrientation",
    },
    "Settings": {"Adapter": "AdapterRead1", "AdapterRead2": "AdapterRead2"},
    "Reads": ["Read1Cycles", "Read2Cycles"],
    "Data": [
        "Sample_ID",
        "IndexI7Name",
        "IndexI7",
        "IndexI5Name",
        "IndexI5",
        "IndexKitName",
    ],
}

data_fields_translate = {"Index": "index", "Index2": "index2"}


def get_bclconvert_app_data(data):
    for app_data in data:
        if app_data["Application"] == "BCLConvert":
            return app_data


def adapters(data_df):
    adapters_read1 = set()
    adapters_read2 = set()

    adapters_read1.update(data_df.get("AdapterRead1", "").strip().split("+"))
    adapters_read2.update(data_df.get("AdapterRead2", "").strip().split("+"))

    adapter_obj = {
        "AdapterRead1": "+".join(adapters_read1),
        "AdapterRead2": "+".join(adapters_read2),
    }

    return adapter_obj


def samplesheet_v1(data_obj, fastq_extraction_tool):

    i5_samplesheet_orientation = data_obj["SampleSheetConfig"][
        "I5SampleSheetOrientation"
    ][fastq_extraction_tool]

    header = {}
    for k, v in samplesheet_v1_template["Header"].items():

        if v in data_obj["Header"]:
            rd_val = data_obj["Header"][v]
            header[k] = rd_val
        else:
            header[k] = v

    header['"FastqExtractionTool'] = fastq_extraction_tool

    reads = []
    for item in samplesheet_v1_template["Reads"]:
        v = data_obj["Reads"][item]
        reads.append(v)

    bclconvert_app = get_bclconvert_app_data(data_obj["Applications"])
    data_df = pd.DataFrame.from_dict(bclconvert_app["Data"])

    if i5_samplesheet_orientation == "rc":
        data_df["IndexI5"] = data_df["IndexI5RC"]

    del data_df["IndexI5RC"]

    settings = adapters(data_df)

    data = data_df[samplesheet_v1_template["Data"]].to_csv(index=False).splitlines()

    output = ["[Header]"]
    output.extend([f"{k},{v}" for k, v in header.items()])

    output.append("")
    output.append("[Settings]")
    output.extend([f"{k},{v}" for k, v in settings.items()])

    output.append("")
    output.append("[Reads]")
    output.extend(reads)

    output.append("")
    output.append("[Data]")
    output.extend(data)

    return "\n".join(output)
