import datetime
import json
import logging
import os
from pathlib import Path

# from random import randint, uniform
import geopandas as gpd
import pystac
from dotenv import load_dotenv
from kanawha_model_data import hms_links, ras_links, ressim_links, storm_view_links
from model_info import (
    get_vol_error,
    sanitize_reference_summary_output,
    sanitize_summary_results_data,
)
from rashdf import RasPlanHdf
from storm_info import storm_info_to_stac_metadata
from utils import (
    create_collection,
    # delete_collection,
    get_basic_object_metadata,
    init_s3_resources,
    list_keys,
    str_from_s3,
    upsert_collection,
    upsert_item,
)

load_dotenv()


BUCKET_NAME = os.getenv("AWS_BUCKET")
KANAWHA_BASIN_SIMPLE_GEOMETRY = f"s3://{BUCKET_NAME}/stac/Kanawha-0505/kanawha.gpkg"
BLOCK_FILE_KEY = "FFRD_Kanawha_Compute/sims/uncertainty_10_by_500_no_bootstrap_5_10a_2024/blockfile_10_by_500.json"
SIMULATION_OUTPUT_PREFIX = "FFRD_Kanawha_Compute/sims/uncertainty_10_by_500_no_bootstrap_5_10a_2024"

COLLECTION_ID = "R001"
REALZIATION = 1


def main(event_ids: list, block_group: int, realization: int = REALZIATION):
    _, client, resource = init_s3_resources()
    event_items = []

    gdf = gpd.read_file(KANAWHA_BASIN_SIMPLE_GEOMETRY, layer="simplified")
    bbox = gdf.total_bounds.tolist()
    geometry = gdf.union_all().__geo_interface__

    for event in event_ids:
        # make sure to include the trailing / in the prefix
        event_prefix = f"{SIMULATION_OUTPUT_PREFIX}/{event}/"
        event_keys = list_keys(client, BUCKET_NAME, event_prefix)

        logging.info(f"Block Group {block_group} | Event {event_prefix}: processing {len(event_keys)} Assets")

        item_id = f"{COLLECTION_ID}-r{realization:03}-e{event:04}"

        item = pystac.Item(id=item_id, geometry=geometry, bbox=bbox, datetime=datetime.datetime.now(), properties={})

        item.properties["metadata_version"] = "Experimental"

        item.validate()
        ras_model_summary = {}
        storm_summary = {}

        for key in event_keys:
            added_roles = []

            key_parts = key.split("/")
            plugin_tag = f"{key_parts[4]}-plugin"
            if plugin_tag == "ras-plugin":
                plugin_tag = "ras-runner-pluign"
            elif plugin_tag == "grids":
                plugin_tag = "map-products-plugin"

            suffix = Path(key).suffix
            file_name = Path(key).name

            bucket_resource = resource.Bucket(BUCKET_NAME)

            s3_metadata = get_basic_object_metadata(bucket_resource.Object(key))

            if suffix == ".log":
                media_type = pystac.MediaType.TEXT
                added_roles.append("simulation-log")

            elif suffix == ".json":
                media_type = pystac.MediaType.JSON
            elif suffix == ".tif":
                media_type = pystac.MediaType.GEOTIFF
            elif suffix == ".met":
                media_type = pystac.MediaType.TEXT
                added_roles.append("sst-data")
                try:
                    storm_summary = storm_info_to_stac_metadata(client, f"s3://{BUCKET_NAME}/{key}")
                except Exception as e:
                    logging.error(f"{file_name}: Failed to get storm info {e}")
            elif suffix == ".grid":
                media_type = pystac.MediaType.TEXT
            elif suffix == ".dss":
                media_type = "application/octet-stream"
            elif suffix == ".hdf":
                media_type = pystac.MediaType.HDF5
                try:
                    ds = RasPlanHdf.open_uri(f"s3://{BUCKET_NAME}/{key}")
                    s3_metadata["hec_ras:volume_error"] = get_vol_error(ds)

                    s3_metadata["hec_ras:summary_output"] = sanitize_summary_results_data(ds)

                    ras_model_summary[file_name] = {
                        "excess_precip_inches": s3_metadata["hec_ras:volume_error"]["Precip Excess (inches)"],
                        "volume_error_pct": s3_metadata["hec_ras:volume_error"]["Error Percent"],
                        # "max_wsel_error": s3_metadata["hec_ras:summary_output"]["Maximum WSEL Error"],
                        "computation_time_minutes": s3_metadata["hec_ras:summary_output"][
                            "Computation Time Total (minutes)"
                        ],
                    }

                    s3_metadata["hec_ras:reference_summary_output"] = sanitize_reference_summary_output(ds)
                    added_roles.append("ras-simulation")
                    logging.info(file_name, s3_metadata["hec_ras:summary_output"]["Computation Time Total (minutes)"])
                except Exception as e:
                    logging.error(file_name, e)

            else:
                media_type = None

            asset = pystac.Asset(
                href=f"s3://{BUCKET_NAME}/{key}",
                media_type=media_type,
                roles=[plugin_tag, *added_roles],
                extra_fields=s3_metadata,
            )

            item.add_asset(file_name, asset)

        # item.add_asset(
        #     "compute-graph",
        #     pystac.Asset(
        #         href=f"https://{BUCKET_NAME}.s3.amazonaws.com/stac/Kanawha-0505/compute-graph.png",
        #         media_type=pystac.MediaType.PNG,
        #         roles=["Thumbnail"],
        #     ),
        # )

        # item.add_asset(
        #     "transposed-storm",
        #     pystac.Asset(
        #         href=f"https://{BUCKET_NAME}.s3.amazonaws.com/stac/Kanawha-0505/transpo.png",
        #         media_type=pystac.MediaType.PNG,
        #         roles=["Thumbnail"],
        #     ),
        # )

        item.add_links([*ras_links, *hms_links, *ressim_links, *storm_view_links])

        item.properties["HEC_HMS:summary"] = "Unavailable"
        item.properties["HEC_ResSIM:summary"] = "Unavailable"

        # item.properties["HEC_RAS:model_failures"] = randint(0, 5)
        item.properties["HEC_RAS:levee_breaches"] = "Unavailable"
        item.properties["HEC_RAS:model_summary"] = ras_model_summary
        item.properties["FFRD:realization"] = REALZIATION
        item.properties["FFRD:block_group"] = block_group
        item.properties["FFRD:event"] = event

        for k, v in storm_summary.items():
            if k == "storm_identification_image":
                item.add_asset(
                    "storm_identification_image",
                    pystac.Asset(
                        href=v,
                        media_type=pystac.MediaType.PNG,
                        roles=["Thumbnail"],
                    ),
                )
            else:
                item.properties[f"FFRD:{k}"] = v

        event_items.append(item)
    return event_items


if __name__ == "__main__":
    collection_id = COLLECTION_ID
    stac_api_url = os.getenv("STAC_API_URL")
    _, client, resource = init_s3_resources()

    sim_records = json.loads(str_from_s3(BLOCK_FILE_KEY, client, BUCKET_NAME))

    for record in sim_records:
        if record["realization_index"] == 1:
            block_group = record["block_index"]
            block_events = range(record["block_event_start"], record["block_event_end"] + 1)
            if block_group == 1:
                logging.info(block_group, list(block_events))
                event_items = main(list(block_events), block_group)
                # WARNING: delete collection as needed to update for testing
                # delete_collection(stac_api_url, collection_id, headers={})
                collection = create_collection(
                    event_items,
                    collection_id,
                    description="This is a sandbox collection for testing purposes",
                    title="sandbox",
                )
                collection.add_asset(
                    "compute-graph",
                    pystac.Asset(
                        href=f"https://{BUCKET_NAME}.s3.amazonaws.com/stac/Kanawha-0505/compute-graph.png",
                        media_type=pystac.MediaType.PNG,
                        roles=["Thumbnail"],
                    ),
                )
                upsert_collection(stac_api_url, collection, headers={})
                for item in event_items:
                    upsert_item(stac_api_url, collection_id, item, headers={})
            else:
                logging.info(block_group, list(block_events))
                event_items = main(list(block_events), block_group)
                for item in event_items:
                    upsert_item(stac_api_url, collection_id, item, headers={})
