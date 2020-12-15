import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

st.title("Motor Vehicle Collisions in New York City 💥🚗")
st.markdown("# This is streamlit dashboard that can be used to analyze moto vehicle collisions data.")

DATA_URL = (
    "E:/TUSHAR ANNAM/Guided_Project/motor_vehicle_collision_web_app/Motor_Vehicle_Collisions_-_Crashes.csv"
    #importing the csv file
)

@st.cache(persist=True) #This decorator is used to automatically rerun the below code when the code input or code is modified., This will help to not run the hole script but just the new or modified block to run.
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE','CRASH_TIME']]) #parse_dates convert string to datetime datatype.
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True) #bydefault inplace=False which creates new object while inplace=True will modify the existing object
    #Pandas dropna() method allows the user to analyze and drop Rows/Columns with Null values
    #in the above code, subset is used to apply dropna function to that specified columns
    lowercase = lambda x: str(x).lower() #used lambda function for converting columns names into lower string format
    data.rename(lowercase, axis="columns", inplace=True)
    data.rename(columns={"crash_date_crash_time": "date/time"}, inplace=True) #renaming big name using dictionary format
    return data

data = load_data(10000)
original_data = data


st.header("Where are the most people injured in New York City")
numberOfInjuredPeople = st.slider("Number of Persons Injured in vehicle collisions",0,20) #we kept the range of slider from 0 to 20
st.map(data.query("injured_persons >= @numberOfInjuredPeople")[["latitude","longitude"]].dropna(how="any")) #injured_persons is the column name in the datatable, to show map latitude and longitude columns should alwys be present.
# .dropna(how="any"), here any is used if there is any null value then delete entire row of it. whereas "all" is used if all the values of a row are  null then delete that row.
# @ is used at the beginning for every variable in query 

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 24)                      #slider
#hour = st.selectbox("Hour to look at", range=(0, 24),1)    #1 is the difference btwn 0 nd 24          #dropdown

original_data = data    #used for selectbox

data = data[data["date/time"].dt.hour == hour]      #extreme right side hour is of the above slider hour and left side is of column of table

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))

st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",  #map theme
    initial_view_state={    #initial bydefault viewing state
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,    #pitch is degree of inclined map here it's 50degree
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[["date/time","latitude","longitude"]],
            get_position=["longitude","latitude"],
            radius=50,  #width of hexagon figure
            extruded=True, #Syntax of 3D figure in map
            #pickable=True,
            elevation_scale=14,  #height of 3d bars
            #elevation_range=[0,1000],
        )
    ]
))



st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data["date/time"].dt.hour >= hour) & (data["date/time"].dt.hour < (hour + 1))
]
hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})

fig = px.bar(chart_data, x="minute", y="crashes", hover_data=["minute", "crashes"], height=400)
st.write(fig)


st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected type of people", ["Pedestrians","Cyclists","Motorists"])

if select == "Pedestrians":
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by=["injured_pedestrians"], ascending=False).dropna(how="any")[:5]) #we want the top 5 data so :5

elif select == "Cyclists":
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name","injured_cyclists"]].sort_values(by=["injured_cyclists"], ascending=False).dropna(how="any")[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name","injured_motorists"]].sort_values(by=["injured_motorists"], ascending=False).dropna(how="any")[:5])


if st.checkbox("Show Raw Data", False): #checkbox is used with False means bydefault unchecked.
    st.header("Raw Data")
    st.write(data)


  


