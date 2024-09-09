import streamlit as st
from datetime import datetime

def init_session_state():
    st.session_state["session_id"] = datetime.now()
    st.session_state["init_data"] = False
