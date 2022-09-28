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
#convert grid cell points to grid cell polygons
for index, row in gridcells.iterrows():
    #for each grid cell point, create a rectangular polygon using point as lower left
    lats = [row.lat, row.lat + latDeg, row.lat + latDeg, row.lat] 
    lons = [row.lon, row.lon, row.lon + lonDeg, row.lon + lonDeg]
    poly_geom = Polygon(zip(lons, lats))
    polys.append(poly_geom)

#storing grid cell polygons in a geodataframe
data = gpd.GeoDataFrame(gridcells['grid cell'], geometry = polys, crs=crs) 


cell = []
distance = []
#check and store closest grid cell for each point
for i, r in popcenters.iterrows():
    point = r['geometry']
    dist = data.distance(point)
    #dist = dist.round(3)
    poly_index = dist.sort_values().index[0]
    cell.append(gridcells['grid cell'].loc[poly_index])
    if min(dist) == 0:
        distance.append("Inside Area")
    else:
        distance.append("Approximation")
    
#save list of gridcells to excel with populations
population['Grid Cell'] = cell
population['In/Out'] = distance
population = population[population['In/Out'] != 'Approximation'] #excludes any points not inside a grid cell
population = population.groupby(population['Grid Cell']).sum() #sums data based on grid cell
population = population['CSD Population 2021']
population = population[population != 0] #remove 0 results

with pd.ExcelWriter('Population Results.xlsx') as writer:
    population.to_excel(writer)