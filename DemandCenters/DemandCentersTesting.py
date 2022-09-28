#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 16:29:49 2022

@author: nathan
"""
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import Point, Polygon
import folium

#Degree spacing between grid cells
latDeg = 0.5
lonDeg = 0.625
crs="EPSG:4326"

#import list of grid cells
path = os.getcwd()
gridcells = pd.read_excel(path + '/coordinate.xlsx')
gridcells.dropna(inplace=True)


#import list of demand centers
population = pd.read_excel(path + '/population-data.xlsx', header=1)
population.dropna(inplace=True)
#create dataframe of points
points = [Point(xy) for xy in zip(population['CSD Rep Point Longitude'], population['CSD Rep Point Latitude'])]
popcenters = gpd.GeoDataFrame(population['CSD Name'], geometry = points, crs=crs) 

polys = []
#convert grid cell points to grid cell objects
for index, row in gridcells.iterrows():
    #for each grid cell point, create a polygon with x degree lat and x degree lon
    lats = [row.lat, row.lat + latDeg, row.lat + latDeg, row.lat]
    lons = [row.lon, row.lon, row.lon + lonDeg, row.lon + lonDeg]
    poly_geom = Polygon(zip(lons, lats))
    polys.append(poly_geom)

data = gpd.GeoDataFrame(gridcells['grid cell'], geometry = polys, crs=crs) 


cell = []
distance = []
dis = []
outside = []
names = []
#check and store closest grid cell for each point
for i, r in popcenters.iterrows():
    point = r['geometry']
    dist = data.distance(point)
    #dist = dist.round(3)
    poly_index = dist.sort_values().index[0]
    dis.append(min(dist))
    cell.append(gridcells['grid cell'].loc[poly_index])
    if min(dist) == 0:
        distance.append("Inside Area")
    else:
        distance.append("Approximation")
        names.append(r['CSD Name'])
        outside.append(point)

#save list of gridcells to excel with populations
population['In/Out'] = distance
population['Distance'] = dis
population['Grid Cell'] = cell

with pd.ExcelWriter('Population Results Testing.xlsx') as writer:
    population.to_excel(writer)


data2 = gpd.GeoDataFrame(names, geometry=outside, crs=crs)
m = folium.Map(location = [-138, 59], tiles='CartoDB positron')

for _, r in data.iterrows():
    # Without simplifying the representation of each borough,
    # the map might not be displayed
    sim_geo = gpd.GeoSeries(r['geometry'])
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j)
    folium.Popup(r['grid cell']).add_to(geo_j)
    geo_j.add_to(m)

    
for _, r in data2.iterrows():
    # Without simplifying the representation of each borough,
    # the map might not be displayed
    sim_geo = gpd.GeoSeries(r['geometry'])
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j)
    folium.Popup(r[0]).add_to(geo_j)
    geo_j.add_to(m)
    
m.save('map.html')