import os

import pystac

SOURCE_URL = "https://kanawha-pilot.s3.amazonaws.com/stac/Kanawha-0505/model_items"
RADIANT_EARTH_PREFIX = "https://radiantearth.github.io/stac-browser/#"
stac_api_url = os.getenv("STAC_API_URL")

ras_links = [
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="BluestoneLocal",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/BluestoneLocal.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="BluestoneUpper",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/BluestoneUpper.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="ElkMiddle",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/ElkMiddle.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="Greenbrier",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/Greenbrier.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="Little",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/Little.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="LowerNew",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/LowerNew.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="ElkRiver",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/ElkSutton.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="GauleyLower",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/GauleyLower.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="GauleySummersville",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/GauleySummersville.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="LowerKanawha",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/LowerKanawha.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="MiddleNew",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/MiddleNew.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="UpperNew",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/UpperNew.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="Coal",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/Coal.json",
        extra_fields={"category": "RAS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_RAS_model",
        title="UpperKanawha",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/UpperKanawha.json",
        extra_fields={"category": "RAS Model"},
    ),
]


hms_links = [
    pystac.Link(
        rel="authoritative_HEC_HMS_model",
        title="Kanwawha",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/LowerNew",
        extra_fields={"category": "HMS Model"},
    ),
    pystac.Link(
        rel="authoritative_HEC_HMS_model",
        title="Kanwawha-POR",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/LowerNew",
        extra_fields={"category": "HMS Model"},
    ),
]


ressim_links = [
    pystac.Link(
        rel="authoritative_HEC_ResSim_model",
        title="Kanwawha",
        target=f"{RADIANT_EARTH_PREFIX}/{SOURCE_URL}/LowerNew",
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
