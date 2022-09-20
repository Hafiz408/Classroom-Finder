import streamlit as st
import pandas as pd

from finder import returnBookKeeping, downloadBookKeeping, downloadSchedule

def viewer():
    cols = st.columns([1,8,1])
    cols[1].title("|.......  Viewer  ......|")
    st.write("")

    bookKeeping = returnBookKeeping()

    st.subheader("Booking Log")
    st.dataframe(bookKeeping)

    st.write("")
    cols = st.columns([3,3,3,3])
    log_btn = cols[1].button(label="Download Logs")
    schedule_btn = cols[2].button(label="Download Schedule")

    if log_btn:
        downloadBookKeeping()
    
    if schedule_btn:
        downloadSchedule()
