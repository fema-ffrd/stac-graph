import datetime
import os
from pathlib import Path
from random import randint, uniform

import geopandas as gpd
import pystac
from dotenv import load_dotenv
from kanawha_model_data import hms_links, ras_links, ressim_links, storm_view_links
from utils import (
    create_collection,
    delete_collection,
    get_basic_object_metadata,
    init_s3_resources,
    list_keys,
    upsert_collection,
    upsert_item,
)

load_dotenv()

BUCKET_NAME = os.getenv("AWS_BUCKET")
KANAWHA_BASIN_SIMPLE_GEOMETRY = f"s3://{BUCKET_NAME}/stac/Kanawha-0505/kanawha.gpkg"


COLLECTION_ID = "Kanawha-0505"
SIMULATION_OUTPUT_PREFIX = "FFRD_Kanawha_Compute/sims/uncertainty_10_by_500_no_bootstrap_5_10a_2024"
REALZIATION = 1
BLOCK_GROUPS = {1: range(1, 5), 2: range(5, 12), 3: range(12, 19)}
# BLOCK_GROUPS = {1: range(1, 2)}


def main():
    _, client, resource = init_s3_resources()
    event_items = []

    gdf = gpd.read_file(KANAWHA_BASIN_SIMPLE_GEOMETRY, layer="simplified")
    bbox = gdf.total_bounds.tolist()
    geometry = gdf.union_all().__geo_interface__

    for block_group, event_ids in BLOCK_GROUPS.items():
        for event in event_ids:
            # make sure to include the trailing / in the prefix
            event_prefix = f"{SIMULATION_OUTPUT_PREFIX}/{event}/"
            event_keys = list_keys(client, BUCKET_NAME, event_prefix)

            print(f"Block Group {block_group} | Event {event_prefix}: processing {len(event_keys)} Assets")

            item_id = f"{COLLECTION_ID}-r{REALZIATION:03}-e{event:04}"

            item = pystac.Item(
                id=item_id, geometry=geometry, bbox=bbox, datetime=datetime.datetime.now(), properties={}
            )

            item.validate()

            for key in event_keys:
                key_parts = key.split("/")
                plugin_tag = key_parts[4]
                if plugin_tag == "ras":
                    plugin_tag = "ras-runner"
                elif plugin_tag == "grids":
                    plugin_tag = "map-products"

                suffix = Path(key).suffix
                file_name = Path(key).name

                bucket_resource = resource.Bucket(BUCKET_NAME)

                s3_metadata = get_basic_object_metadata(bucket_resource.Object(key))

                ras_log_file = False
                if suffix == ".log":
                    media_type = pystac.MediaType.TEXT
                    ras_model_name = Path(key).parent.name
                    ras_log_file = True
                    asset_key_name = f"{ras_model_name}-simulation.log"
                elif suffix == ".json":
                    media_type = pystac.MediaType.JSON
                elif suffix == ".tif":
                    media_type = pystac.MediaType.GEOTIFF
                elif suffix == ".met":
                    media_type = pystac.MediaType.TEXT
                elif suffix == ".grid":
                    media_type = pystac.MediaType.TEXT
                elif suffix == ".dss":
                    media_type = "application/octet-stream"
                elif suffix == ".hdf":
                    media_type = pystac.MediaType.HDF5
                    s3_metadata["hec_ras:excess_precip"] = "1.3"
                    s3_metadata["hec_ras:volume_error"] = f"{uniform(0,1)}%"
                    s3_metadata["hec_ras:gages_peak_flow"] = {
                        "gage_1": randint(100000, 200000),
                        "gage_2": randint(1000, 5000),
                    }
                else:
                    media_type = None

                asset = pystac.Asset(
                    href=f"s3://{BUCKET_NAME}/{key}",
                    media_type=media_type,
                    roles=[plugin_tag],
                    extra_fields=s3_metadata,
                )

                if ras_log_file:
                    item.add_asset(asset_key_name, asset)
                else:
                    item.add_asset(file_name, asset)

            item.add_asset(
                "compute-graph",
                pystac.Asset(
                    href=f"https://{BUCKET_NAME}.s3.amazonaws.com/stac/Kanawha-0505/compute-graph.png",
                    media_type=pystac.MediaType.PNG,
                    roles=["Thumbnail"],
                ),
            )

            item.add_asset(
                "transposed-storm",
                pystac.Asset(
                    href=f"https://{BUCKET_NAME}.s3.amazonaws.com/stac/Kanawha-0505/transpo.png",
                    media_type=pystac.MediaType.PNG,
                    roles=["Thumbnail"],
                ),
            )

            item.add_links([*ras_links, *hms_links, *ressim_links, *storm_view_links])

            # From the .grid file
            year, month, day = randint(1979, 2023), randint(1, 12), randint(1, 28)

            item.properties["SST:historic_storm_date"] = f"{year}-{month:02}-{day:02}"
            item.properties["SST:historic_storm_year_rank"] = randint(1, 10)
            item.properties["SST:historic_storm_rank"] = randint(1, 440)
            item.properties["SST:historic_storm_center"] = (
                f"POINT({uniform(bbox[1],bbox[3])}, {uniform(bbox[0],bbox[2])})"
            )
            item.properties["SST:modeled_event_center"] = (
                f"POINT({uniform(bbox[1],bbox[3])}, {uniform(bbox[0],bbox[2])})"
            )
            # item.properties["SST:modeled_event_center"] = f"POINT(38.635, -81.347)"
            item.properties["SST:modeled_event_temperature_sample_date"] = f"{year}-{month:02}-{day:02}"

            item.properties["HEC_HMS:total_excess_precip"] = str(uniform(0, 3))
            item.properties["HEC_HMS:total_excess_precip_units"] = "inches"
            item.properties["HEC_HMS:total_error"] = f"{uniform(0,3)}%"

            item.properties["HEC_RAS:model_failures"] = randint(0, 5)
            item.properties["HEC_RAS:levee_breaches"] = randint(0, 3)
            item.properties["HEC_RAS:model_summary"] = {
                "BluestoneLocal": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "BluestoneUpper": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "ElkMiddle": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "Greenbrier": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "Little": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "LowerNew": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "ElkRiver_at_Sutton": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "GauleyLower": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "GauleySummersville": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "LowerKanawha": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "MiddleNew": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "UpperNew": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "Coal": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
                "UpperKanawha": {"excess_precip": str(uniform(0, 3)), "volume_error": f"{uniform(0,1)}%"},
            }

            item.properties["FFRD:realization"] = REALZIATION
            item.properties["FFRD:block_group"] = block_group
            item.properties["FFRD:event"] = event
            item.properties["FFRD:status"] = "Experimental"

            event_items.append(item)
    return event_items


if __name__ == "__main__":
    collection_id = COLLECTION_ID
    stac_api_url = os.getenv("STAC_API_URL")
    event_items = main()
    # WARNING: delete collection as needed to update for testing
    # delete_collection(stac_api_url, collection_id, headers={})
    test_collection = create_collection(
        event_items,
        collection_id,
        description="Kanawha Pilot test collection for Realization 1. \
            This collection is a sandbox for development and testing, much of the data has been mocked for development purposes.",
        title="Kanawha-R1",
    )
    upsert_collection(stac_api_url, test_collection, headers={})
    for item in event_items:
        upsert_item(stac_api_url, collection_id, item, headers={})
