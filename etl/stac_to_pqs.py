import os
import sys
from pathlib import Path

import pandas as pd
from pystac_client import Client

stac_url = os.getenv("STAC_API_URL")
stac_client = Client.open(stac_url)
stac_collections = ["None"] + [collection.id for collection in stac_client.get_collections()]
collection_id = "Kanawha-0505-R001"
item_data = []


def storms_data_to_df(data):
    return pd.DataFrame(data)


def extract_computation_data(item, counter=0):
    computation_data = {}
    for k, data in item.properties["HEC_RAS:model_summary"].items():
        data["primary_key"] = counter
        data["realization"] = item.properties["FFRD:realization"]
        data["event"] = item.properties["FFRD:event"]
        data["block_group"] = item.properties["FFRD:block_group"]
        data["ID"] = item.id
        data["ras_model"] = k
        computation_data[counter] = data
        counter += 1
    return computation_data


def extract_storm_data(item):
    return {
        "ID": item.id,
        "event": item.properties.get("FFRD:event", "N/A"),
        "block_group": item.properties.get("FFRD:block_group", "N/A"),
        "realization": item.properties.get("FFRD:realization", "N/A"),
        "SST_storm_center": item.properties.get("FFRD:SST_storm_center", "N/A"),
        "historic_storm_date": item.properties.get("FFRD:historic_storm_date", "N/A"),
        "historic_storm_center": item.properties.get("FFRD:historic_storm_center", "N/A"),
        "historic_storm_season": item.properties.get("FFRD:historic_storm_season", "N/A"),
        "historic_storm_max_precip_inches": item.properties.get("FFRD:historic_storm_max_precip_inches", "N/A"),
    }


def extract_gage_data(item, counter=0):
    gage_data = {}
    for a in item.get_assets(role="ras-simulation"):
        asset = item.assets[a]
        summary = asset.extra_fields.get("hec_ras:reference_summary_output", "N/A")
        for mesh_name, gages in summary.items():
            for gage, data in gages.items():
                data["primary_key"] = counter
                data["ras_model"] = Path(asset.href).name[:-8]
                data["realization"] = item.properties["FFRD:realization"]
                data["event"] = item.properties["FFRD:event"]
                data["block_group"] = item.properties["FFRD:block_group"]
                data["ID"] = item.id
                data["gage"] = gage
                gage_data[counter] = data
                counter += 1
    return gage_data


def main(collection_id: str):
    storm_data = []
    gage_data, gage_data_counter = {}, 0
    computation_data, computation_data_counter = {}, 0

    for i, item in enumerate(stac_client.get_collection(collection_id).get_all_items()):
        print(i, item.id)
        try:
            storm_data.append(extract_storm_data(item))
        except Exception as e:
            print(f"Error extracting storm data: {e}")

        try:
            gage_data.update(extract_gage_data(item, counter=gage_data_counter))
        except Exception as e:
            print(f"Error extracting gage data: {e}")

        try:
            computation_data.update(extract_computation_data(item, counter=computation_data_counter))
        except Exception as e:
            print(f"Error extracting computation data: {e}")

        try:
            computation_data_counter = max(computation_data.keys())
        except ValueError:
            print("No computation data found")

        try:
            gage_data_counter = max(gage_data.keys())
        except ValueError:
            print("No gage data found")

        # if i == 30:
        #     break

    return storm_data, gage_data, computation_data


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1:
        realization = args[0]
    else:
        print("please enter realization (1-5) for Kanawha")

    collection_id = f"Kanawha-0505-R00{realization}"
    storm_data, gage_data, computation_data = main(collection_id)

    storms_df = storms_data_to_df(storm_data)
    storms_df.to_parquet(f"storms-{collection_id}.parquet", engine="pyarrow")

    gages_df = pd.DataFrame.from_records(gage_data).T
    gages_df.to_parquet(f"gages-{collection_id}.parquet", engine="pyarrow")

    computation_df = pd.DataFrame.from_records(computation_data).T
    computation_df.to_parquet(f"computation-{collection_id}.parquet", engine="pyarrow")
