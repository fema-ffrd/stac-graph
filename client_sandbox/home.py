import os

import pandas as pd
import streamlit as st
from components.layout import configure_page_settings, render_footer
from config.settings import LOG_LEVEL
from utils.stac_data import init_computation_data, init_gage_data, init_storm_data
from utils.session import init_session_state

GAGES_DATA = "s3://kanawha-pilot/stac/Kanawha-0505/data-summary/gages.pq"
STORMS_DATA = "s3://kanawha-pilot/stac/Kanawha-0505/data-summary/storms.pq"
COMPUTATION_DATA = "s3://kanawha-pilot/stac/Kanawha-0505/data-summary/computation.pq"


def app():
    """Main app function for the Streamlit home page."""
    configure_page_settings("Home")
    st.title("Kanawha Pilot Sandbox")
    st.markdown(
        """
        This viewer is a sandbox for exploring the Kanawha Pilot data. The data is stored in a
        SpatioTemporal Asset Catalog (STAC) and is accessible via the STAC API. The data is
        organized into three main categories: gages, storms, and computations. The gages data
        contains information about the gages in the Kanawha Pilot study area. The storms data
        contains information about the storms that have been processed. The computations data
        contains information about the computations that have been run. Use the sidebar to
        navigate between the different data categories.
        """
    )
    if "session_id" not in st.session_state:
        init_session_state()
    st.stac_url = st.secrets.STAC_API_URL

    st.session_state.log_level = LOG_LEVEL

    if st.session_state["init_data"] is False:
        st.write("Initializing datasets...")
        init_gage_data(GAGES_DATA)
        init_storm_data(STORMS_DATA)
        init_computation_data(COMPUTATION_DATA)
        st.session_state["init_data"] = True
        st.balloons()
        st.success("Complete! Data is ready for exploration.")

    if st.session_state["init_data"] is True:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Gages")
            st.write(st.gages.head())
        with col2:
            st.write("Storms")
            st.write(st.storms.head())
        with col3:
            st.write("Computations")
            st.write(st.computation.head())

    render_footer()


if __name__ == "__main__":
    app()
