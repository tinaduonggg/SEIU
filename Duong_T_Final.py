"""
Name: Tho (Tina) Duong
UID: 704818150
Date: June 12, 2019
Final Project: Service Area Analysis for SEIU-UHW Dialysis Campaign

This python script and function utilizes the core concepts of GEOG 173 to automate both processes of routing matrix
and service area analysis. This project uses open source data to aggregate csv documentations of dialysis clinics and
SEIU United Healthcare Workers' offices in the state of California. By producing interactive webmaps with html files,
this project is specifically useful to organizers and workers organizing with SEIU UHW, especially those involved in
the ongoing Dialysis Campaign to struggle against unfair wages and predatory practices of dialysis companies.

The first map will plot all dialysis clinics in California, from which the campaign started. It will include a
heat map to illustrate the concentration of dialysis, along with points mapping SEIU UHW offices in California.

The second map will use the use input of latitude, longitude of the location of their choice and the range of driving
time. According to these inputs, the function will request service area analysis services from OpenRouteService to
create isochrones showing the area reachable in the time interval chosen by the user, from their originating latitude
and longitude. Additionally, the function will request routing services from the same API to map out the recommended
routes from their location to all of the clinics within the driving time isochrones.

I hope to improve upon this project in the near future to validate input of latitude and longitude within the bounds
of the state of California. For now, however, any input outside of the state of California may not return reachable
clinics resulting from the service area analysis. Furthermore, I would like to upload the html files onto a public
server. Unfortunately, I was unable to connect to the  BruinOnLine WebSpace FTP.
"""


import requests
import pandas as pd
from openrouteservice import client
import folium
from shapely.geometry import Polygon, Point, mapping
from folium.plugins import MeasureControl, FloatImage, HeatMap, MarkerCluster

# prompt user to input lat and long
running = True
while running:
    lat = input("Enter the latitude of your location in California: ")
    try:
        lat = float(lat)
    except:
        print("Please only enter valid latitude values.")
        continue
    if 90 < lat or lat < -90:
        print("Please enter a valid value for your latitude [-90,90]!")
    elif -90 <= lat <= 90:
        running = False
        continue
running = True
while running:
    lon = input("Enter the longitude of your location in California: ")
    try:
        lon = float(lon)
    except:
        print("Please only enter valid longitude values.")
        continue
    if 180 < lon or lon < -180:
        print("Please enter a valid value for your longitude [-180, 180]!")
    elif -180 <= lon <= 180:
        running = False
        continue
# prompt user to input time range for driving isochrones
running = True
while running:
    time = input("Enter your range for driving time in minute(s) (maximum: 60 minutes): ")
    try:
        time = int(time)
    except ValueError:
        print("Please only enter numbers.")
        continue
    if time > 60:
        print("Please enter a range less than 60 minutes")
    elif time <= 60:
        running = False
        continue


# pass parameters into function
def seiu(lat, lon, time):
    print("")
    # request reverse geocoding
    r = requests.get('https://api.opencagedata.com/geocode/v1/json?q=%s+%s&key=7e95a1a406154911b68bfff0a5bf9c34'
                     % (lat, lon))
    results = r.json()
    where = results['results'][0]['formatted']
    print("Your location is:", where)

    # load csv
    df_ca = pd.read_csv('supporting documents/Dialysis_CA.csv')
    df_la = pd.read_csv('supporting documents/Dialysis_LA.csv')
    df_seiu = pd.read_csv('supporting documents/SEIU_UHW_CA.csv')

    # handle lat lon as floats
    df_seiu['lat'] = df_seiu['lat'].astype(float)
    df_seiu['lon'] = df_seiu['lon'].astype(float)

    df_ca['lat'] = df_ca['lat'].astype(float)
    df_ca['lon'] = df_ca['lon'].astype(float)

    df_la['lat'] = df_la['lat'].astype(float)
    df_la['lon'] = df_la['lon'].astype(float)

    # map
    map = folium.Map(location=[36.7783, -119.4179],
                     tiles='Stamen Toner',
                     zoom_start=5.5)

    # plugin for MeasureControl
    map.add_child(MeasureControl())

    # float image plugin for logo
    logo = ('https://i.imgur.com/WTmLCbc.png')
    justice = ('https://i.imgur.com/mJgkwHV.png')
    FloatImage(logo, bottom=8, left=4).add_to(map)
    FloatImage(justice, bottom=.5, left=4).add_to(map)

    fg = folium.FeatureGroup(name='Heat Map of Dialysis Clinics').add_to(map)
    heat_df = df_ca[['lat', 'lon']]
    heat_data = [[row['lat'], row['lon']] for index, row in heat_df.iterrows()]
    HeatMap(heat_data, radius=15, blur=17).add_to(fg)

    # clinics in CA
    clinic_df = df_ca[['lat', 'lon']]
    clinic_data = [[r['lat'], r['lon']] for i, r in clinic_df.iterrows()]

    fg_1 = folium.FeatureGroup(name='Dialysis Clinics').add_to(map)
    marker_cluster = MarkerCluster().add_to(fg_1)

    for point in range(0, len(clinic_data)):
        folium.Marker(clinic_data[point],
                      popup='<strong>' + "Facility: " + df_ca['Facility N'][point] + " - Address:"'</strong>'
                            + df_ca['Address Li'][point],
                      icon=folium.Icon(color='beige', icon_color='darkpurple', icon='plus')).add_to(marker_cluster)

    # SEIU offices
    seiu_df = df_seiu[['lat', 'lon']]
    seiu_data = [[r['lat'], r['lon']] for i, r in seiu_df.iterrows()]

    fg_2 = folium.FeatureGroup(name='SEIU UHW Offices').add_to(map)
    for point in range(0, len(seiu_data)):
        folium.Marker(seiu_data[point],
                      popup='<strong>' + "SEIU Office: " + df_seiu['SEIU UHW'][point] + " - Address:" '</strong>'
                            + df_seiu['Address'][point], icon=folium.Icon(color='darkpurple', icon_color='white',
                                                                          icon='heart')).add_to(fg_2)

    folium.LayerControl(collapsed=False).add_to(map)

    map.save('MapFinal1.html')

    # Service Area
    loc = [[lon, lat]]
    loc_df = pd.DataFrame(loc, columns=['lon', 'lat'])
    org_df = loc_df[['lat', 'lon']]
    org_data = [[r['lat'], r['lon']] for i, r in org_df.iterrows()]

    map2 = folium.Map(location=[float(lat), float(lon)],
                      tiles='Stamen Toner',
                      zoom_start=11)

    FloatImage(logo, bottom=8, left=4).add_to(map2)
    FloatImage(justice, bottom=.5, left=4).add_to(map2)

    for point in range(0, len(org_data)):
        folium.Marker(org_data[point],
                      popup='<strong>' "Your Input Location:" + where + '</strong>',
                      icon=folium.Icon(color='darkpurple', icon_color='white', icon='user')).add_to(map2)

    key = '5b3ce3597851110001cf6248c13297498fc24a73a4067bd7d1a87f7d'
    clnt = client.Client(key=key)

    # parameters for isochrones request
    params_iso = {'profile': 'driving-car',
                  'range': [time * 60],
                  'interval': time * 60}
    loc_dict = {'loc': {'location': [lon, lat]}}

    for name, loc in loc_dict.items():
        params_iso['locations'] = [loc['location']]
        iso = clnt.isochrones(**params_iso)
        folium.features.GeoJson(iso).add_to(map2)

    iso_buffer = Polygon(iso['features'][0]['geometry']['coordinates'][0])
    folium.features.GeoJson(data=mapping(iso_buffer), name='Drive Time Isochrone', overlay=True).add_to(map2)

    # reverse lat lon df
    clinic_r_a = df_ca[['lat', 'lon', 'Address Li', 'Facility N']]
    clinic_r_a_data = [[r['lon'], r['lat'], r['Address Li'], r['Facility N']] for i, r in clinic_r_a.iterrows()]

    print("")
    print("Clinics within" + " " + str(time) + " " + "minute(s) of driving" + ": ")
    print("")
    for clinic in clinic_r_a_data:
        point = Point(clinic)
        if iso_buffer.contains(point):
            omglol = clinic[3] + " at " + clinic[2]
            folium.Marker(list(reversed(point.coords[0])), popup='<strong>' + "Clinics within" + " " + str(time) + " " +
                                                                 "minute(s) of driving" + '</strong>' + ": " + omglol,
                          icon=folium.Icon(color='beige', icon_color='darkpurple', icon='plus')).add_to(map2)

    params_route = {'profile':'driving-car',
                    'format_out': 'geojson',
                    'geometry':'true',
                    'format':'geojson',
                    'instructions':'true',
                    'preference':'recommended'}

    def style_function(color):
        return lambda feature: dict(color=color, weight=3, opacity=1)

    for clinic in clinic_r_a_data:
        point = Point(clinic)
        for name, loc in loc_dict.items():
            org_coord = loc['location']
        if iso_buffer.contains(point):
            omglol = clinic[3] + " at " + clinic[2]
            clinic_coord = [clinic[0], clinic[1]]
            params_route['coordinates'] = [org_coord, clinic_coord]
            json_route = clnt.directions(**params_route)
            folium.features.GeoJson(json_route, style_function=style_function("#ffff00")).add_to(map2)
            folium.Marker(list(reversed(point.coords[0])), popup='<strong>' + "Clinics within" + " " + str(time) + " " +
                                                                 "minute(s) of driving" + '</strong>' + ": " + omglol,
                          icon=folium.Icon(color='beige', icon_color='darkpurple', icon='plus')).add_to(map2)
            print(omglol)
            print("Driving distance in minute(s):")
            print((json_route['features'][0]['properties']['summary']['duration'])/60)
            print("")

    map2.save('MapFinal2.html')


seiu(lat,lon,time)


