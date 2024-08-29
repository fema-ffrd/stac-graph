import os

import pystac

RADIANT_EARTH_PREFIX = "https://radiantearth.github.io/stac-browser/#"
stac_api_url = os.getenv("STAC_API_URL")

ras_links = [
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="BluestoneLocal",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/BluestoneLocal",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="BluestoneUpper",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/BluestoneUpper",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="ElkMiddle",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/ElkMiddle",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="Greenbrier",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/Greenbrier",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="Little",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/Little",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="LowerNew",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/LowerNew",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="ElkRiver_at_Sutton",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/ElkRiver_at_Sutton",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="GauleyLower",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/GauleyLower",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="GauleySummersville",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/GauleySummersville",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="LowerKanawha",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/LowerKanawha",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="MiddleNew",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/MiddleNew",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="UpperNew",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/UpperNew",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="Coal",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/Coal",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="UpperKanawha",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/UpperKanawha",
        extra_fields={"category": "RAS Model"},
    ),
]


hms_links = [
    pystac.Link(
        rel="authoritative_HEC_HMS_model",
        title="Kanwawha",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/LowerNew",
        extra_fields={"category": "HMS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_HMS_model",
        title="Kanwawha-POR",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/LowerNew",
        extra_fields={"category": "HMS Model"},
    ),
]


ressim_links = [
    pystac.Link(
        rel="authoritative_HEC_ResSim_model",
        title="Kanwawha",
        target=f"{RADIANT_EARTH_PREFIX}{stac_api_url}/collections/kanawha-models-march-2024/items/LowerNew",
        extra_fields={"category": "HMS Model"},
    )
]

storm_view_links = [
    pystac.Link(
        rel="storms_database",
        title="AORC 4km Storms Catalog",
        target="https://storms.dewberryanalytics.com",
        extra_fields={"category": "Data Viewer"},
    )
]
