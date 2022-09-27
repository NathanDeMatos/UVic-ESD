#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 11:17:46 2022

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
poly = area['geometry'].unary_union
df = gpd.GeoDataFrame()
df['geometry'] = [poly]

points = [Point(xy) for xy in zip(nodes.longitude, nodes.latitude)]
nodes.drop(['latitude', 'longitude'], axis = 1, inplace=True)

data = gpd.GeoDataFrame(nodes.node_code, geometry=points)
data.crs = "EPSG:4326"
data = data.merge(nodes)

final = gpd.GeoDataFrame(columns = ['name', 'node_code', 'geometry'])

for index, row in data.iterrows():
    point = row['geometry']
    if poly.contains(point):
        final = final.append(data.iloc[index])
        
base = df.plot()
final.plot(ax=base, marker='o', color='red', markersize=5)