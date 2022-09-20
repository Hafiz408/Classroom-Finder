import streamlit as st
import pandas as pd

df = pd.read_excel('Classrooms excel.xlsx', sheet_name='Sheet2')
df.drop(columns=df.columns[-5:], axis=1, inplace=True)
df.dropna(subset=['Hall\Hour'], inplace=True)
df['capacity'] = df['Hall\Hour'].str.split('(').str[1].str[:-1]
df['capacity'] = pd.to_numeric(df['capacity'])
df['hall'] = df['Hall\Hour'].str.split('(').str[0].str[:-1]
df.drop(columns='Hall\Hour', axis=1, inplace=True)
df['block'] = df['hall'].str[0]
df['day'] = 'Friday'

bookKeeping = pd.DataFrame()

def callback():
    st.session_state.button_clicked = True

def updateBookKeeping(record, bookKeeping):
    bookKeeping = bookKeeping.append(record, ignore_index=True)
    return bookKeeping

def classroomFinder(day,hour,capacity,block):
  grp = df.groupby(['day']).get_group(day)
  if len(block) > 0:
    grp = grp[['hall',hour]][(grp['capacity'] >= capacity) & (grp[hour].isnull()) & (grp['block'].isin(block))]
  else:
    grp = grp[['hall',hour]][(grp['capacity'] >= capacity) & (grp[hour].isnull())]
  res = list(grp['hall'])
  return res

def bookClass(classroom, day, **kwargs):
    hour = int(kwargs['hour'])
    df[hour][(df['day'] == day) & (df['hall'] == classroom)] = 'BOOKED' + '_' + kwargs['year'] + '_' + kwargs['course'].upper() + '-' + kwargs['section']
    return True

def schedule_class():
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False

    # st.image("doc 1.jpeg")
    cols = st.columns([1,8,1])
    cols[1].title("|.......  Finder  ......|")
    st.write("")

    name = st.text_input("Name :")
    rollNo = st.text_input("Roll No :")
    year = st.selectbox("Year :",['nan', '1', '2', '3', '4', '5'])
    course = st.selectbox("Course :",['nan', 'DS', 'TCS', 'SS'])
    section = st.selectbox("Section :",['nan', 'G1', 'G2'])
    phone = st.text_input("Phone No :")
    date = st.date_input('Day :')
    hour = st.selectbox("Hour :",['nan', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])

    capacity = st.selectbox("Minimun Capacity :",['nan', '< 40', '40', '60', '80', '> 100'])
    block = st.multiselect("Block :",['nan', 'A', 'G', 'J', 'E'])

    bookerInfo = { 'name': name, 'rollNo': rollNo, 'year': year, 'course': course, 'section': section, 'phone': phone, 'date': date, 'hour': hour, 'capacity': capacity, 'block': block }

    st.write("")
    cols = st.columns([3,2,3])
    ok = cols[1].button(label="Find Available Halls", on_click=callback)

    if ok or st.session_state.button_clicked:
        day = bookerInfo['date'].strftime('%A')
        hour = int(bookerInfo['hour'])
        block = bookerInfo['block']
        capacity = bookerInfo['capacity']
        if capacity == 'nan':
            capacity = 60
        else:
            capacity = int(capacity[-3:])

        freeRooms = classroomFinder(day, hour, capacity, block)
        if len(freeRooms) == 0:
            st.error('No halls available !!')
        else:
            freeRooms.insert(0,'Choose anyone of the available halls from dropdown')
            classroom = st.selectbox("Available Halls :", freeRooms)

        st.write("")
        cols = st.columns([3,1,3])
        book_button = cols[1].button(label="Book hall")

        if book_button:
            if len(classroom) < 5:
                if bookClass(classroom, day, **bookerInfo):
                    st.success('Classroom {} booked !!'.format(classroom))
                    bookerInfo['day'] = day
                    bookerInfo['hall'] = classroom
                    global bookKeeping
                    bookKeeping = updateBookKeeping(bookerInfo, bookKeeping)
                    st.dataframe(bookKeeping)
                    st.session_state.button_clicked = False
                    st.balloons()
            else:
                st.warning('Choose anyone of the available halls !!')
