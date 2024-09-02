import os

import pandas as pd
import streamlit as st
from components.layout import configure_page_settings, render_footer
from config.settings import LOG_LEVEL
from dotenv import load_dotenv
from utils.stac_data import fetch_collection_data, generate_stac_item_link

GAGES_DATA = "s3://kanawha-pilot/stac/Kanawha-0505/data-summary/gages.pq"
STORMS_DATA = "s3://kanawha-pilot/stac/Kanawha-0505/data-summary/storms.pq"
COMPUTATION_DATA = "s3://kanawha-pilot/stac/Kanawha-0505/data-summary/computation.pq"


def collection_id(realization):
    return f"Kanawha-0505-R{realization:03}"


def app():
    """Main app function for the Streamlit home page."""
    configure_page_settings("Home")

    load_dotenv()
    st.stac_url = os.getenv("STAC_API_URL")

    st.session_state.log_level = LOG_LEVEL
    st.storms = pd.read_parquet(STORMS_DATA, engine="pyarrow")
    st.storms["Link"] = st.storms.apply(
        lambda row: f'<a href="{generate_stac_item_link(st.stac_url, collection_id(row["realization"]), row["ID"])}" target="_blank">See in Catalog</a>',
        axis=1,
    )

    st.gages = pd.read_parquet(GAGES_DATA, engine="pyarrow")
    st.gages["Link"] = st.gages.apply(
        lambda row: f'<a href="{generate_stac_item_link(st.stac_url, collection_id(row["realization"]), row["ID"])}" target="_blank">See in Catalog</a>',
        axis=1,
    )

    st.computation = pd.read_parquet(COMPUTATION_DATA, engine="pyarrow")

    st.markdown(
        """
        Sandbox for interacting with STAC data from the Kanawha Pilot.
        """
    )

    render_footer()


if __name__ == "__main__":
    app()
