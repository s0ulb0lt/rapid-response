import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from covplan import pathplan
from covplan import find_min
import math
import json

st.set_page_config(
    page_title="Rapid Response Dash",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'coords_array' not in st.session_state:
    st.session_state['coords_array'] = []

if 'angle' not in st.session_state:
    st.session_state['angle'] = 90

if 'people_found' not in st.session_state:
    st.session_state['people_found'] = []

if 'plan' not in st.session_state:
    st.session_state['plan'] = 0

st.sidebar.text_input("Mission Altitude", key="m_alt")
st.sidebar.text_input("Mission Speed", key="m_spd")

with st.form('update_map'):
    map_view = folium.Map(location=[37.4116716675053, -121.9964139161828], zoom_start=16)
    if not st.session_state["people_found"] == 0:
        for person in st.session_state["people_found"]:
            folium.Marker(
                [person[1], person[2]], popup="Person", tooltip="Person"
            ).add_to(map_view)
    if not st.session_state['plan'] == 0:
        line = folium.PolyLine(locations=st.session_state['plan'], color='blue', weight=2, opacity=0.8).add_to(map_view)
    with open("people.txt", "r") as file:
        people_array = [line.strip() for line in file]
        if len(people_array) >= 1:
            for i in people_array:
                line_array = i.split("\t")
                folium.Marker(
                    [float(line_array[1]) / float(10 ** 7), float(line_array[2]) / float(10 ** 7)], popup=line_array[0]
                ).add_to(map_view)
    folium.Marker(
        [-35.363143, 149.165243], popup="37.4116716675053, -121.9964139161828", tooltip="Home"
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
    st.form_submit_button("Submit Map Data (WILL END ANY RUNNING MISSIONS!!)")

if st.button("Generate Mission"):
    st.session_state['plan'] = 0
    n_clusters = 1
    r=10
    inp_file = 'mission.txt'
    width = 2.00 * math.tan(math.degrees(127/2)) * float(st.session_state['m_alt']) - 2.00
    no_hd = 0

    st.session_state['angle']=find_min(inp_file, width=width, num_hd=no_hd, num_clusters=n_clusters, radius=r, verbose=True)

    st.session_state['plan'] = pathplan(inp_file, num_hd=no_hd, width=width, radius=r, theta=st.session_state['angle'], num_clusters=n_clusters, visualize=False)
    print("Trajectory: ", st.session_state['plan'])

    with open("formatted_mission.txt", "w") as file:
        file.write("QGC WPL 110")
        file.write("0\t" + "1\t" + "0\t" + "16\t" + "0\t" + "0\t" + "0\t" + "0\t" + "0\t" + "0\t" + "2\t" + "1" + "\t\n")
        file.write("1\t" + "0\t" + "3\t" + "178\t" + "0\t" + str(st.session_state["m_spd"]) + "\t" + "0\t" + "0\t" + "0\t" + "0\t" + "0\t" + "1" + "\t\n")
        file.write("2\t" + "0\t" + "3\t" + "22\t" + "0\t" + "0\t" + "0\t" + "0\t" + "0\t" + "0\t" + str(st.session_state["m_alt"]) + "\t" + "1" + "\t\n")
        counter = 2
        for x in st.session_state['plan']:
            counter += 1
            file.write(str(counter) + "\t" + "0\t" + "3\t" + "16\t" + "0\t0\t0\t0\t" + str(x[0]) + "\t" + str(x[1]) + "\t" + str(st.session_state['m_alt']) + "\t" + "1" + "\t\n")
        file.write(str(counter+1) + "\t" + "0\t" + "3\t" + "20\t" + "0\t" + "0\t" + "0\t" + "0\t" + "0\t" + "0\t" + "0" + "\t" + "1" + "\t\n")

    # return_dict = {
    #     "fileType": "Plan",
    #     "geoFence": {
    #         "circles": [],
    #         "polygons": [],
    #         "version": 2
    #     },
    #     "groundStation": "QGroundControl",
    #     "mission": {
    #         "cruiseSpeed": int(st.session_state['m_spd']),
    #         "firmwareType": 3,
    #         "hoverSpeed": 5,
    #         "items": [
    #             {
    #                 "AMSLaltAboveTerrain": None,
    #                 "command": 22,
    #                 "doJumpId": 1,
    #                 "frame": 3,
    #                 "params": [
    #                     0.0,
    #                     0.0,
    #                     0.0,
    #                     0.0,
    #                     0.0,
    #                     0.0,
    #                     int(st.session_state['m_alt'])
    #                 ],
    #                 "type": "SimpleItem"
    #             }
    #         ],
    #         "plannedHomePosition": [st.session_state['plan'][0][0], st.session_state['plan'][0][0]],
    #         "vehicleType": 2,
    #         "version": 1
    #     },
    #     "rallyPoints": {
    #         "points": [],
    #         "version": 2
    #     },
    #     "version": 1
    # }

    # for i in st.session_state['plan']:
    #     mission_points = return_dict["mission"]["items"]
    #     mission_points.append(
    #         {
    #             "autoContinue": True,
    #             "command": 16,
    #             "doJumpId": 0,
    #             "frame": 3,
    #             "params": [
    #                 0.0,
    #                 0.0,
    #                 0.0,
    #                 0.0,
    #                 i[0],
    #                 i[1],
    #                 int(st.session_state['m_alt'])
    #             ],
    #             "type": "SimpleItem"
    #         }
    #     )
    
    # return_dict["mission"]["items"].append(
    #     {
    #         "autoContinue": True,
    #         "command": 20,
    #         "doJumpId": 0,
    #         "frame": 3,
    #         "params": [
    #             0.0,
    #             0.0,
    #             0.0,
    #             0.0,
    #             0.0,
    #             0.0,
    #             0.0
    #         ]
    #     }
    # )

    # with open("mission.json", "w") as file:
    #     json.dump(return_dict, file, indent=4)

