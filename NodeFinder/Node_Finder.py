#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 13:54:48 2022

@author: nathan
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

province = 'Ontario'

raw_node_data = pd.read_csv(r"/home/nathan/UVic-ESD/NodeFinder/CODERS-Nodes.csv")
raw_node_data = raw_node_data[raw_node_data['planning_region']==province]

nodes = pd.DataFrame(raw_node_data[['name', 'node_code', 'latitude', 'longitude']])

area = gpd.read_file(r"/home/nathan/UVic-ESD/NodeFinder/Neighbourhoods - 4326.geojson")
area = area.to_crs(4326)

trans = gpd.read_file("/home/nathan/UVic-ESD/NodeFinder/all_transformer_servicearea.shp")
trans = trans.to_crs(4326)

points = [Point(xy) for xy in zip(nodes.longitude, nodes.latitude)]
nodes.drop(['latitude', 'longitude'], axis = 1, inplace=True)

data = gpd.GeoDataFrame(nodes.node_code, geometry=points)
data.crs = "EPSG:4326"
data = data.merge(nodes)

final = gpd.GeoDataFrame(columns = ['name', 'node_code', 'geometry'], crs='EPSG:4326')
neighborhood = []
transformer = []
distance = []

#check if points are in neighborhoods, remove points that are not
for i, r in area.iterrows():
    poly = r['geometry']
    for index, row in data.iterrows():
        point = row['geometry']
        if poly.contains(point):
            final = final.append(data.iloc[index])
            neighborhood.append(r.AREA_NAME)                

#find closest transformer area to each point
for index, row in final.iterrows():
    point = row['geometry']
    test = trans.distance(point)
    poly_index = test.sort_values().index[0]
    transformer.append(trans['Name'].loc[poly_index])
    if min(test) == 0:
        distance.append("Inside Area")
    else:
        distance.append("Approximation")

final['Neighborhood'] = neighborhood
final['Transformer Area'] = transformer
final['Location'] = distance

base = trans.plot()
final.plot(ax=base, marker='o', color='red', markersize=5)

final.drop(['geometry'], axis=1, inplace=True)
final.to_excel("/home/nathan/UVic-ESD/NodeFinder/Nodes_in_location.xlsx")