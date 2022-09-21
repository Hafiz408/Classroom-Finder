import datetime
import streamlit as st
import pandas as pd
import numpy as np

from constants import courses, hours

def read_excel_sheets():
    df = pd.DataFrame()
    for sheet in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
        day_df = pd.read_excel('Classroom schedule.xlsx', sheet_name=sheet)
        day_df['day'] = sheet.capitalize()
        df = df.append(day_df, ignore_index=True)
    return df

df = read_excel_sheets()
df.dropna(subset=['Hall\Hour'], inplace=True)
df['capacity'] = df['Hall\Hour'].str.split('(').str[1].str[:-1]
df['capacity'] = pd.to_numeric(df['capacity'])
df['hall'] = df['Hall\Hour'].str.split('(').str[0].str[:-1]
df.drop(columns='Hall\Hour', axis=1, inplace=True)
df['block'] = df['hall'].str[0]

blocks = list(sorted(df['block'].unique()))
blocks.insert(0, 'Any')

bookKeeping = pd.DataFrame()

def callback():
    st.session_state.button_clicked = True

def callback2():
    if st.session_state.continuous_hour_checkbox:
        st.session_state.continuous_hour_checkbox = False
    else:
        st.session_state.continuous_hour_checkbox = True

def updateBookKeeping(record, bookKeeping):
    bookKeeping = bookKeeping.append(record, ignore_index=True)
    return bookKeeping

def returnBookKeeping():
    return bookKeeping

def returnSchedule():
    return df

def check_booked_halls(freeRooms, **kwargs):
    if bookKeeping.empty or (kwargs['date'] not in bookKeeping['date'].values):
        return freeRooms
    grp = bookKeeping.groupby(['date']).get_group(kwargs['date'])
    start_hour, end_hour = kwargs['start hour'], kwargs['end hour']
    grp = grp[( ((grp['start hour'] <= start_hour) & (grp['end hour'] >= end_hour)) | ((grp['start hour'] <= start_hour) & (grp['end hour'] <= end_hour)) | ((grp['start hour'] >= start_hour) & (grp['end hour'] <= end_hour)) | ((grp['start hour'] >= start_hour) & (grp['end hour'] >= end_hour)) ) & ~((grp['end hour'] < start_hour) | (grp['start hour'] > end_hour))]
    res = list(grp['hall'])
    freeRooms = list(set(freeRooms).difference(res))
    return freeRooms


def classroomFinder(day,hour,capacity,block):
    df.replace('nan', np.nan, inplace=True)
    grp = df.groupby(['day']).get_group(day)
    if not isinstance(hour,int):
        hours = [ i for i in range(int(hour[0]), int(hour[1])+1)]
        cols = hours.copy()
        cols.insert(0, 'hall')
        if len(block) > 0:
            if 'Any' in block:
                grp = grp[cols][(grp['capacity'] >= capacity) & (grp[hours].isnull().all(axis=1))]
            else:
                grp = grp[cols][(grp['capacity'] >= capacity) & (grp[hours].isnull().all(axis=1)) & (grp['block'].isin(block))]
        else:
            grp = grp[cols][(grp['capacity'] >= capacity) & (grp[hours].isnull().all(axis=1))]
    else:
        if len(block) > 0:
            if 'Any' in block:
                grp = grp[['hall',hour]][(grp['capacity'] >= capacity) & ((grp[hour].isnull()) | (grp[hour] == 'nan'))]
            else:
                grp = grp[['hall',hour]][(grp['capacity'] >= capacity) & ((grp[hour].isnull()) | (grp[hour] == 'nan')) & (grp['block'].isin(block))]
        else:
            grp = grp[['hall',hour]][(grp['capacity'] >= capacity) & ((grp[hour].isnull()) | (grp[hour] == 'nan'))]
    res = list(grp['hall'])
    return res

def schedule_class():
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False
    
    if 'continuous_hour_checkbox' not in st.session_state:
        st.session_state.continuous_hour_checkbox = False
    
    cols = st.columns([1,8,1])
    cols[1].title("|.......  Finder  ......|")
    st.write("")

    name = st.text_input("Name :")

    cols = st.columns([1,1])
    rollNo = cols[0].text_input("Roll No :")
    year = cols[1].selectbox("Year :",['', '1', '2', '3', '4', '5'])

    cols = st.columns([1,1])
    course = cols[0].selectbox("Course :", sorted(courses))
    section = cols[1].selectbox("Section :",['', 'None', 'G1', 'G2'])

    phone = st.text_input("Phone No :")

    cols = st.columns([1,1])
    date = cols[0].date_input('Day :')
    hour = cols[1].selectbox("Hour :", hours, disabled=st.session_state.continuous_hour_checkbox)
    
    cols = st.columns([1,1])
    continuous_hour_checkbox = cols[1].checkbox('Book for continuous hours', on_change=callback2)
    start_hour = end_hour = ''
    if continuous_hour_checkbox:
        hour = ''
        cols = st.columns([1,1])
        start_hour = cols[0].selectbox("Start hour :", hours)
        end_hours = hours[hours.index(start_hour)+1:]
        end_hours.insert(0, '')
        end_hour = cols[1].selectbox("End hour :", end_hours)

    cols = st.columns([1,1])
    capacity = cols[0].selectbox("Minimun Capacity :",['Optional', '< 40', '40', '60', '80', '> 100'])
    block = cols[1].multiselect("Block :", blocks, default='Any')

    today = datetime.date.today()
    if date < today:
        st.warning('Attempting Time travel ?')

    day = date.strftime('%A')

    bookerInfo = { 'name': name, 'rollNo': rollNo, 'year': year, 'course': course, 'section': section, 'phone': phone, 'date': date, 'day': day, 'hour': hour, 'capacity': capacity, 'block': block }

    st.write("")
    cols = st.columns([3,2,3])
    ok = cols[1].button(label="Find Available Halls", on_click=callback)

    if ok or st.session_state.button_clicked:
        if day == 'Saturday' or day == 'Sunday':
            st.warning("Can't book hall on {}".format(day))
            st.session_state.button_clicked = False
        elif len(name) == 0 or len(rollNo) == 0 or len(year) == 0 or len(course) == 0 or len(section) == 0 or len(phone) == 0 or not date or (len(hour) == 0 and (len(start_hour) == 0 or len(end_hour) == 0)):
            st.warning('Fill the required details !!')
            st.session_state.button_clicked = False
        else:
            if len(bookerInfo['hour']) != 0:
                hour = int(bookerInfo['hour'])
                bookerInfo['hour'] = hour
            else:
                hour = [int(start_hour), int(end_hour)]
                bookerInfo['start hour'] = hour[0]
                bookerInfo['end hour'] = hour[1]
            block = bookerInfo['block']
            capacity = bookerInfo['capacity']
            if capacity == 'Optional':
                capacity = 60
            else:
                capacity = int(capacity[-3:])

            freeRooms = classroomFinder(day, hour, capacity, block)
            if bookerInfo['hour'] != '':
                bookerInfo['start hour']= bookerInfo['end hour'] = bookerInfo['hour']
            bookerInfo.pop('hour')

            freeRooms = check_booked_halls(freeRooms, **bookerInfo)

            if len(freeRooms) == 0:
                st.error('No halls available !!')
                st.session_state.book_btn = True
            else:
                freeRooms.insert(0,'Choose anyone of the available halls from dropdown')
                classroom = st.selectbox("Available Halls :", sorted(freeRooms))
                st.session_state.book_btn = False

            st.write("")
            cols = st.columns([3,1,3])
            book_button = cols[1].button(label="Book hall", disabled=st.session_state.book_btn)

            if book_button:
                if len(classroom) < 6:
                    st.success('Classroom {} booked for hour {} !!'.format(classroom, hour))
                    bookerInfo['hall'] = classroom
                    global bookKeeping
                    bookKeeping = updateBookKeeping(bookerInfo, bookKeeping)
                    st.session_state.button_clicked = False
                    st.balloons()
                else:
                    st.warning('Choose anyone of the available halls !!')
