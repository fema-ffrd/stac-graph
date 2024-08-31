import json
import logging

import requests
from pyproj import Transformer
from utils import split_s3_key, str_from_s3

STORM_SEARCH_URL = "https://storms.dewberryanalytics.com/meilisearch/indexes/events/search"
WATERSHED = "Kanawha"
SST_REGION_VERSION = "V01"

PROJECTION = """PROJCS["USA_Contiguous_Albers_Equal_Area_Conic_USGS_version",
								GEOGCS["NAD83",
									DATUM["North_American_Datum_1983",
										SPHEROID["GRS 1980",6378137,298.257222101,
											AUTHORITY["EPSG","7019"]],
										AUTHORITY["EPSG","6269"]],
									PRIMEM["Greenwich",0,
										AUTHORITY["EPSG","8901"]],
									UNIT["degree",0.0174532925199433,
										AUTHORITY["EPSG","9122"]],
									AUTHORITY["EPSG","4269"]],
								PROJECTION["Albers_Conic_Equal_Area"],
								PARAMETER["latitude_of_center",23],
								PARAMETER["longitude_of_center",-96],
								PARAMETER["standard_parallel_1",29.5],
								PARAMETER["standard_parallel_2",45.5],
								PARAMETER["false_easting",0],
								PARAMETER["false_northing",0],
								UNIT["metre",1,
									AUTHORITY["EPSG","9001"]],
								AXIS["Easting",EAST],
								AXIS["Northing",NORTH],
								AUTHORITY["EPSG","5070"]]
            """


def convert_to_storm_center_epsg4326(x, y, wkt):
    transformer = Transformer.from_crs(wkt, "EPSG:4326", always_xy=True)
    x, y = transformer.transform(x, y)
    return f"POINT({y} {x})"


# def get_storm_info(s3_uri):
#     """FROM .grid file"""
#     results = {}
#     bucket_name, key = split_s3_key(s3_uri)
#     data = str_from_s3(key, client, bucket_name).split("\n")
#     storm_date_index = data.index("     Grid Type: Precipitation\r") - 1
#     storm_info = data[storm_date_index].replace("Grid: ", "").replace("\r", "").split(" ")
#     results["storm_date"] = storm_info[1]
#     results["water_year_rank"] = int(storm_info[2].replace("Y", ""))

#     for line in data:
#         if "Storm Center X" in line:
#             x = float(line.split(":")[1].strip().replace("\r", ""))
#         elif "Storm Center Y" in line:
#             y = float(line.split(":")[1].strip().replace("\r", ""))

#     if x and y:
#         results["sst_storm_center"] = convert_to_storm_center_epsg4326(x, y, PROJECTION)
#     else:
#         print("No Storm center..")
#     return results


def get_storm_info(s3_uri, client):
    """FROM .met file"""
    results = {}
    bucket_name, key = split_s3_key(s3_uri)
    data = str_from_s3(key, client, bucket_name).split("\n")
    for line in data:
        if "     Precip Grid Name:" in line:
            storm_info = line.split("Precip Grid Name:")[1].replace("\r", "").split(" ")
            results["storm_date"] = storm_info[2]
            results["water_year_rank"] = int(storm_info[3].replace("Y", ""))
        elif "Storm Center X" in line:
            x = float(line.split(":")[1].strip().replace("\r", ""))
        elif "Storm Center Y" in line:
            y = float(line.split(":")[1].strip().replace("\r", ""))

    if x and y:
        results["sst_storm_center"] = convert_to_storm_center_epsg4326(x, y, PROJECTION)
    else:
        logging.warning("No Storm center..")
    return results


def storm_viewer_query(watershed_name: str, transposition_region_ver: str, year: int, water_year_rank: int):

    query_params = {
        "facets": [
            "ranks.declustered_rank",
            "stats.mean",
            "start.calendar_year",
            "start.water_year",
            "start.season",
            "duration",
            "categories.lv10",
            "categories.lv11",
        ],
        "filter": [
            [f'categories.lv10="{watershed_name}"'],
            [f'start.calendar_year="{year}"'],
            f"ranks.declustered_rank>={water_year_rank}",
            f"ranks.declustered_rank<={water_year_rank}",
        ],
        "sort": ["start.timestamp:asc"],
    }

    r = requests.post(STORM_SEARCH_URL, json=query_params)
    try:
        r.raise_for_status()
    except Exception as e:
        raise ValueError(r.content.decode()) from e
    data = json.loads(r.content)

    if not data["hits"]:
        raise ValueError("No storm found")
    else:
        return data["hits"][0]


def storm_info_to_stac_metadata(client, s3_key, watershed_name: str = "Kanawha", transposition_region_ver: str = "V01"):
    try:
        sim_data = get_storm_info(s3_key, client)
        storm_year = sim_data["storm_date"].split("-")[0]
        storm_rank = sim_data["water_year_rank"]
        sst_storm_center = sim_data["sst_storm_center"]
    except Exception as e:
        logging.error(e)
        return {}
    try:
        storm_data = storm_viewer_query(
            watershed_name, transposition_region_ver, year=storm_year, water_year_rank=storm_rank
        )
        return {
            "historic_storm_date": storm_data["start"]["datetime"],
            "historic_storm_season": storm_data["start"]["season"],
            "historic_storm_max_precip_inches": round(storm_data["stats"]["max"], 2),
            "historic_storm_center": f'POINT({storm_data["geom"]["center_y"]} {storm_data["geom"]["center_x"]})',
            "SST_storm_center": sst_storm_center,
            f'{storm_data["start"]["datetime"].replace("-","")}.png': storm_data["metadata"]["png"],
        }

    except Exception as e:
        logging.error(e)
        return {}
