from pymavlink import mavutil
import csv
import streamlit as st
import pandas as pd
import numpy as np
import time
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from covplan import pathplan
from covplan import find_min
from ultralytics import YOLO

st.set_page_config(
    page_title="Rapid Response Dash",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'drone' not in st.session_state:
    st.session_state['drone'] = 0

if 'coords_array' not in st.session_state:
    st.session_state['coords_array'] = []

if 'counter' not in st.session_state:
    st.session_state['counter'] = 0

if 'plan' not in st.session_state:
    st.session_state['plan'] = 0

if 'angle' not in st.session_state:
    st.session_state['angle'] = 90

def connect(): 
    try:
        st.session_state.drone.wait_heartbeat()
        st.sidebar.write("Heartbeat (system %u component %u)" % (st.session_state.drone.target_system, st.session_state.drone.target_component))
        st.session_state["connected"] = True
    except AttributeError as error:
        st.sidebar.write(f"Please connect First!: {error}")

@st.cache_resource
def get_model(model):
    return YOLO(model)

@st.fragment
def run_coverage():
    print(len(st.session_state["plan"]))
    for i in st.session_state["plan"]:
        st.session_state.drone.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(10, st.session_state.drone.target_system, st.session_state.drone.target_component, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, int(0b110111111000), int(float(i[0]) * 10 ** 7), int(float(i[1]) * 10 ** 7), 30, 0, 0, 0, 0, 0, 0, 0, 0))
        nextPass = False
        while not nextPass:
            msg = st.session_state.drone.recv_match(type="NAV_CONTROLLER_OUTPUT", blocking=True)
            if (msg.wp_dist == 0):
                nextPass = True
def arm_and_takeoff(alt):
    st.session_state.drone.mav.command_long_send(st.session_state.drone.target_system, st.session_state.drone.target_component,
                                  mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, 1, 4, 0, 0, 0, 0, 0)

    msg = st.session_state.drone.recv_match(type='COMMAND_ACK', blocking=True)
    print(msg)

    st.session_state.drone.mav.command_long_send(st.session_state.drone.target_system, st.session_state.drone.target_component,
                                  mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)


    armed = 1

    while armed != 0:
        msg = st.session_state.drone.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg)
        armed = msg.result

    st.session_state.drone.mav.command_long_send(st.session_state.drone.target_system, st.session_state.drone.target_component,
                                  mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, int(alt))
    st.session_state.drone.mav.command_long_send(st.session_state.drone.target_system, st.session_state.drone.target_component,
                                  mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 0, 20, 0, 0, 0, 0, 0)

    msg = st.session_state.drone.recv_match(type='COMMAND_ACK', blocking=True)
    print(msg)

def move_to(lat, lon, alt):
    st.session_state.drone.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(10, st.session_state.drone.target_system, st.session_state.drone.target_component, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, int(0b110111111000), int(float(lat) * 10 ** 7), int(float(lon) * 10 ** 7), float(alt), 0, 0, 0, 0, 0, 0, 0, 0))

def return_to_home():
    st.session_state.drone.mav.command_long_send(st.session_state.drone.target_system, st.session_state.drone.target_component,
                                  mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, 1, 6, 0, 0, 0, 0, 0)

    msg = st.session_state.drone.recv_match(type='COMMAND_ACK', blocking=True)
    print(msg)

if 'connected' not in st.session_state:
    st.session_state["connected"] = False

st.sidebar.text_input("Connect URL", key="inp_url")
if st.sidebar.button('Connect', disabled=st.session_state.get("connected", True)):
    st.session_state["drone"] = mavutil.mavlink_connection(st.session_state.inp_url)

test_connection = st.sidebar.button('Test Connection', on_click=connect)

st.sidebar.text_input("Original Takeoff Altitude", key="tkf_alt")
arm_button = st.sidebar.button('Arm and Takeoff', on_click=arm_and_takeoff, args=(st.session_state["tkf_alt"], ))

st.sidebar.text_input("Move To Lat", key="mv_lat")
st.sidebar.text_input("Move To Lon", key="mv_lon")
st.sidebar.text_input("Move To Alt", key="mv_alt")
mv_button = st.sidebar.button('Move To', on_click=move_to, args=(st.session_state["mv_lat"], st.session_state["mv_lon"], st.session_state["mv_alt"])) 

rtl_button = st.sidebar.button('Return To Landing', on_click=return_to_home)

@st.fragment
def update_map():
    try:
        results = get_model("yolo11n_RUN").track(source="0", show=True)
        st.rerun(scope="fragment")
    except:
        st.write("No camera connection found")
    map_view = folium.Map(location=[-35.363143, 149.165243], zoom_start=16)
    if not st.session_state['plan'] == 0:
        line = folium.PolyLine(locations=st.session_state['plan'], color='blue', weight=2, opacity=0.8).add_to(map_view)
    # for i in st.session_state['plan']:
    #     folium.Marker(
    #         [i[0], i[1]], popup=st.session_state['plan'].index(i)
    #     ).add_to(map_view)
    folium.Marker(
        [-35.363143, 149.165243], popup="-35.363143, 149.165243", tooltip="Home"
    ).add_to(map_view)
    Draw(export=True).add_to(map_view)
    st_data = st_folium(map_view, use_container_width=True, height=1000)
    try:
        if st_data["all_drawings"][0]["geometry"]["type"] == "Polygon" and st.session_state["coords_array"] == []:
            with open('mission.txt', 'w') as txtfile:
                for i in st_data["all_drawings"][0]["geometry"]["coordinates"][0]:
                    st.session_state["coords_array"].append([i[1], i[0]])
                    txtfile.write(" ".join([str(i[1]), str(i[0])]) + "\n")
                st.write(st.session_state["coords_array"])
                txtfile.write("NaN NaN")
    except IndexError as error:
        st.session_state["coords_array"] = []
        with open('mission.txt', 'w') as txtfile:
            txtfile.write("")
    except TypeError as error:
        st.write("Please Draw a Polygon (Clockwise)")

update_map()

if st.button("Generate Mission"):
    st.session_state['plan'] = 0
    n_clusters = 1
    r=10
    inp_file = 'mission.txt'
    width = 30
    no_hd = 0

    st.session_state['angle']=find_min(inp_file, width=width, num_hd=no_hd, num_clusters=n_clusters, radius=r, verbose=True)

    st.session_state['plan'] = pathplan(inp_file, num_hd=no_hd, width=width, radius=r, theta=st.session_state['angle'], num_clusters=n_clusters, visualize=False)
    print("Trajectory: ", st.session_state['plan'])

if st.button("Run Mission"):
    if not st.session_state['plan'] == 0:
        run_coverage()