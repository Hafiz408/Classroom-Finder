import streamlit as st
import pandas as pd

from finder import schedule_class
from admin import viewer

col1,col2 = st.sidebar.columns([4,3])
# col1.image("doc 2.jpeg",width=120)
col2.write("")
col2.write("")
col2.write("")
col2.write("""# Finder""")   
st.sidebar.write("")
st.sidebar.write("")

choice = st.sidebar.radio("Menu",['Schedule', 'Viewer'])

if choice == 'Schedule':
    schedule_class()
else:
    viewer()
