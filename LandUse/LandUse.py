#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 14:15:49 2022

@author: nathan
"""
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import Polygon
import folium

# Degree spacing between grid cells
latDeg = 0.5
lonDeg = 0.625

crs = "EPSG:4326"  # Careful which CRS is used, will affect results
layer = ["Critical", 'High', 'Medium']
path = os.getcwd()


# import map data
m = gpd.read_file(path + '/Wind_Solar_Directive_Project.shp')
labels = m.query('Wind_Direc != @layer').Wind_Direc
m = m.set_index(m.Wind_Direc, drop=True)
m = m.drop(labels)
m = m.to_crs(crs=crs)

# import list of grid cells
gridcells = pd.read_excel(path + '/coordinate.xlsx')
gridcells.dropna(inplace=True)

polys = []
# convert grid cell points to grid cell polygons
for index, row in gridcells.iterrows():
    # for each grid cell point, create a rectangular polygon using point as lower left
    lats = [row.lat, row.lat + latDeg, row.lat + latDeg, row.lat]
    lons = [row.lon, row.lon, row.lon + lonDeg, row.lon + lonDeg]
    poly_geom = Polygon(zip(lons, lats))
    polys.append(poly_geom)

# storing grid cell polygons in a geodataframe
data = gpd.GeoDataFrame(gridcells['grid cell'], geometry=polys, crs=crs)
data['initial_area'] = data.area


# check overlap between all grid cells
allowed_area = data.overlay(m, how='difference')
allowed_area = allowed_area.to_crs(crs=crs)
allowed_area['final_area'] = allowed_area.area
allowed_area['percent_area'] = allowed_area.final_area / \
    allowed_area.initial_area


mp = folium.Map(location = [-138, 59], tiles='CartoDB positron')

for _, r in allowed_area.iterrows():
    # Without simplifying the representation of each borough,
    # the map might not be displayed
    sim_geo = gpd.GeoSeries(r['geometry'])
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j)
    folium.Popup(r['grid cell']).add_to(geo_j)
    geo_j.add_to(mp)

mp.save('map.html')


with pd.ExcelWriter('Area Results EPSG:4326.xlsx') as writer:
    allowed_area.to_excel(writer)
