"""Make a PNG of a storm event in the Kanawha Basin."""

import os

import geopandas as gpd
import xarray as xr
from matplotlib import pyplot as plt


def main():
    BUCKET_NAME = os.getenv("AWS_BUCKET")
    NOAA_AORC_DATA_URL = "https://noaa-nws-aorc-v1-1-1km.s3.amazonaws.com"
    TRANSPO_REGION_FILE = "s3://tempest/watersheds/kanawha/kanawha-transpo-area-v01.geojson"
    KANAWHA_BASIN_SIMPLE_GEOMETRY = f"s3://{BUCKET_NAME}/stac/Kanawha-0505/kanawha.gpkg"

    gdf_transpo_region = gpd.read_file(TRANSPO_REGION_FILE)
    gdf = gpd.read_file(KANAWHA_BASIN_SIMPLE_GEOMETRY, layer="simplified")

    # Constrain the data to the bounding box of the Kanawha Transposition Region
    bbox = gdf_transpo_region.total_bounds
    # bbox = gdf.total_bounds

    year, month, day = 1985, 5, 17
    data_url = f"{NOAA_AORC_DATA_URL}/{year}.zarr"

    ds = xr.open_dataset(data_url, engine="zarr")

    start, stop = f"{year}-{month}-{day}", f"{year}-{month}-{day+2}"
    data = (
        ds["APCP_surface"]
        .sel(time=slice(start, stop), longitude=slice(bbox[0], bbox[2]), latitude=slice(bbox[1], bbox[3]))
        .sum(dim="time")
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 10))

    data.plot.pcolormesh(x="longitude", y="latitude", ax=ax1)
    gdf.plot(ax=ax1, edgecolor="black", color="none", linewidth=2)
    gdf_transpo_region.plot(ax=ax1, edgecolor="gray", color="none", linewidth=2)

    data.shift(latitude=80, longitude=-500).plot.pcolormesh(x="longitude", y="latitude", ax=ax2)
    gdf.plot(ax=ax2, edgecolor="black", color="none", linewidth=2)
    # gdf_centerpoint.plot(ax=ax, marker="*", markersize=500, color="red")
    gdf_transpo_region.plot(ax=ax2, edgecolor="gray", color="none", linewidth=2)
    fig.savefig(f"kanawha-storm-{start}-{stop}.png")


if __name__ == "__main__":
    main()
