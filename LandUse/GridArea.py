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

crs_list = ["EPSG:4326", "EPSG:6933", "EPSG:3857"] # Careful which CRS is used, will affect results
path = os.getcwd()

# import list of grid cells
gridcells = pd.read_excel(path + '/coordinate.xlsx')
gridcells.dropna(inplace=True)

polys = []
# convert grid cell points to grid cell polygons
for index, row in gridcells.iterrows():
    #for each grid cell point, create a rectangular polygon using point as lower left
    lats = [row.lat, row.lat + latDeg, row.lat + latDeg, row.lat] 
    lons = [row.lon, row.lon, row.lon + lonDeg, row.lon + lonDeg]
    poly_geom = Polygon(zip(lons, lats))
    polys.append(poly_geom)


# storing grid cell polygons in a geodataframe
data = gpd.GeoDataFrame(gridcells['grid cell'], geometry = polys)
data['lat'] = gridcells.lat 


#Checking different CRS
for crs in crs_list:
    data_temp = data.set_crs(crs, allow_override=True).copy()
    colname = ('area_' + crs)
    data[colname] = data_temp.area
    
    
data = data.drop('geometry', axis=1)