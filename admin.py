import streamlit as st
import pandas as pd
import io

from finder import returnBookKeeping, returnSchedule

buffer = io.BytesIO()

def convert_to_excel(df):
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer)
        writer.save()
        return buffer

def viewer():
    cols = st.columns([1,8,1])
    cols[1].title("|.......  Viewer  ......|")
    st.write("")

    bookKeeping = returnBookKeeping()
    schedule = returnSchedule()

    st.subheader("Booking Log")
    st.dataframe(bookKeeping)

    if not bookKeeping.empty:
        log_data = convert_to_excel(bookKeeping)

        st.write("")
        cols = st.columns([3,3,3])
        cols[1].download_button(label="Download Logs", data=log_data, file_name="Booking log.xlsx", mime="application/vnd.ms-excel")
