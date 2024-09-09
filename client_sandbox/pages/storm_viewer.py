import os

import folium
import geopandas as gpd
import streamlit as st
from components.layout import configure_page_settings
from components.tables import stylized_table
from shapely import wkt
from shapely.geometry import Point
from streamlit_folium import st_folium


def swap_coordinates(point_str):
    """Fix for error in stac items, need to fix in catalog and return wkt.loads(point_str)"""
    point = wkt.loads(point_str)
    return Point(point.y, point.x)


def app():
    configure_page_settings("Storm Viewer")

    st.markdown("## Storm Viewer")

    df = st.storms.rename(
        columns={
            "block_group": "Block",
            "historic_storm_date": "Date",
            "historic_storm_season": "Season",
            "historic_storm_max_precip_inches": "Max Precip (in)",
            "realization": "Realization",
            "date": "Date",
        }
    )

    search_col1, search_col2 = st.columns(2)

    with search_col1:
        realization = st.number_input("Search by Realization", min_value=0, max_value=5, step=1)
        search_block = st.number_input("Search by Block Group", min_value=0, step=1)
        search_id = st.text_input("Search by ID")

    with search_col2:
        search_precip_inches = st.number_input("Search by Max Precipitation (inches)", min_value=0.0, step=0.1)
        storm_season = st.selectbox("Search for Seasonal Storms", ["All", "spring", "summer", "fall", "winter"])
        enable_date_search = st.checkbox("Enable Date Search")
        search_storm_date = None
        if enable_date_search:
            search_storm_date = st.date_input("Search by Storm Date")

    if search_block:
        df = df[df["Block"] == search_block]
    if realization > 0:
        df = df[df["Realization"] == realization]
    if search_id:
        df = df[df["ID"].str.contains(search_id, case=False, na=False)]
    if search_precip_inches:
        df = df[df["Max Precip (in)"] >= search_precip_inches]
    if search_storm_date:
        df = df[df["Date"].str.contains(search_storm_date.strftime("%Y-%m-%d"), case=False, na=False)]
    if storm_season != "All":
        df = df[df["Season"].str.contains(storm_season, case=False, na=False)]

    col1, col2 = st.columns([2, 1])

    with col1:
        stylized_table(
            df[
                [
                    "ID",
                    "Realization",
                    "Block",
                    "Max Precip (in)",
                    "Date",
                    "Season",
                    "Link",
                ]
            ]
        )

    with col2:

        try:
            df["geometry"] = df["historic_storm_center"].apply(swap_coordinates)
            gdf = gpd.GeoDataFrame(df, geometry="geometry")
        except Exception as e:
            st.error(f"Error creating GeoDataFrame: {e}")
            return

        try:
            df["geometry2"] = st.storms["SST_storm_center"].apply(swap_coordinates)
            gdf2 = gpd.GeoDataFrame(df[["ID"]], geometry=df["geometry2"])
        except Exception as e:
            st.error(f"Error creating secondary GeoDataFrame: {e}")
            gdf2 = None

        m = folium.Map(location=[37.75153, -80.94911], zoom_start=6)

        folium.GeoJson(f"{st.stac_url}/collections/Kanawha-0505-R001/items/R001-E2044").add_to(m)

        st.dataframe(gdf)
        # historic_storm_center
        for idx, row in gdf.iterrows():
            if isinstance(row.geometry, Point):
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=5,
                    color="blue",
                    fill=True,
                    fill_color="blue",
                    popup=f"Historic Center: {row['ID']}",
                ).add_to(m)

        # SST_storm_center
        if gdf2 is not None:
            st.dataframe(gdf2)
            for idx, row in gdf2.iterrows():
                if isinstance(row.geometry, Point):
                    folium.CircleMarker(
                        location=[row.geometry.y, row.geometry.x],
                        radius=5,
                        color="red",
                        fill=True,
                        fill_color="red",
                        popup=f"SST Center: {row['ID']}",
                    ).add_to(m)

        st_folium(m, width=350, height=500)


if __name__ == "__main__":
    app()
