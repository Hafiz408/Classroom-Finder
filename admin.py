import streamlit as st
import pandas as pd

def viewer():
    cols = st.columns([1,8,1])
    cols[1].title("|.......  Viewer  ......|")
    st.write("")

    st.dataframe(bookKeeping)
