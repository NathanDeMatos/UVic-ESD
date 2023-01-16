#!/usr/bin/env python
# coding: utf-8

"""
Created on Jul 25 14:15:49 2022

@author: nathan
"""

import collections 
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from pathlib import Path

#%%
province = 'BC' #set the desired province
planning_region = 'British Columbia'

# Map Settings
map_mode = 'Main' # Options are All, Main, AlgoCheck
name_nodes = 'Main' # Options are All, Main, None

# For AlgoCheck
checkNode = 'BC_GCL_DSS' # Node to check for AlgoCheck
oldNode = "BC_MSA_DSS" # Old node that checkNode was aggregated to

#%%
# Defining Functions

# Function to create geopandas dataframe with lines between nodes,
def mapLines(data):  #given a dataframe with 2 sets of lon/lat co-ords
    geometry = [LineString(xy) for xy in zip(zip(data['lon1'], data['lat1']), zip(data['lon2'], data['lat2']))]
    geo_df = gpd.GeoDataFrame(data, crs = {'init':'EPSG:4326'}, geometry = geometry)
    return geo_df #returns a geopandas dataframe with the line geometries assigned

# Function to create geopandas dataframe of points at each node
def mapPoints(data): #given a dataframe with one set of lon/lat co-ords
    geometry = [Point(xy) for xy in zip(data['lon1'], data['lat1'])]
    geo_df = gpd.GeoDataFrame(data, crs = {'init':'EPSG:4326'}, geometry = geometry)
    return geo_df

# Adds the latitude and longitude co-ordinates to each node in a dataframe
def nodeLatLon(df, nodes): #given a dataframe and column headings for each set of nodes
    i = 1
    for bus in nodes:
        df = pd.merge(df, node_lookup, how = 'left', left_on = bus, right_on  = 'node')
        df = df.rename(columns = {'lat':'lat'+ str(i), 'lon':'lon'+ str(i)})
        i = i + 1
    return df

# Recursive function to create dictionary of parent nodes (to find shortest path)
def findPath(node, start, pathDict): #given a starting node, main node and an empty defaultdict
    parent = parentdf.loc[node][start]
    
    if parent == -1:
        return
    
    findPath(parent, start, pathDict)
    
    pathDict[node] = parent
    
    return pathDict


def algoCheck(node, old, ax):
    new = final2.at[node, 'new_bus']
    pathDict1 = collections.defaultdict(dict) #dictionary of edges and vertices (graph)
    path1 = findPath(node, new, pathDict1)
    newPath = pd.DataFrame.from_dict(path1, orient='index')
    newPath.reset_index(inplace=True)
    newPath = newPath.rename(columns = {'index':'start_node', 0:'end_node'})
    newerPath = nodeLatLon(newPath, ['start_node', 'end_node'])
    mapNewPath = mapLines(newerPath)
    mapNewPath.plot(ax=ax, color = 'orange')
    
    pathDict2 = collections.defaultdict(dict) #dictionary of edges and vertices (graph)
    path2 = findPath(node, old, pathDict2)
    oldPath = pd.DataFrame.from_dict(path2, orient='index')
    oldPath.reset_index(inplace=True)
    oldPath = oldPath.rename(columns = {'index':'start_node', 0:'end_node'})
    olderPath = nodeLatLon(oldPath, ['start_node', 'end_node'])
    mapOldPath = mapLines(olderPath)
    mapOldPath.plot(ax=ax, color = 'purple')
    return

#%%
main_path = str(Path().resolve().parent)
path = f"{main_path}/Data"

final = pd.read_excel(f'{main_path}/Results/Aggregated_nodes_{province}.xlsx', sheet_name = province)
main = pd.read_excel(f'{main_path}/Results/Aggregated_nodes_{province}.xlsx', sheet_name = 'main_nodes')
lines = pd.read_excel(f'{main_path}/Results/Aggregated_nodes_{province}.xlsx', sheet_name = 'lines')
parentdf = pd.read_excel(f'{main_path}/Results/Aggregated_nodes_{province}.xlsx', sheet_name = 'parents')
parentdf = parentdf.set_index(['Unnamed: 0'])

node_lookup = pd.read_csv(f"{path}/CODERS-Nodes.csv", usecols=['node_code', 'latitude', 'longitude', 'planning_region'])
node_lookup = node_lookup.query(f'planning_region == "{planning_region}"')
node_lookup = node_lookup.drop('planning_region', axis=1)
node_lookup.columns = ['node', 'lat', 'lon']

final.columns = ['old_bus', 'new_bus']
final2 = final.copy()
final2 = final2.set_index(['old_bus'])

main = nodeLatLon(main, ['node'])
lines = nodeLatLon(lines, ['start_node', 'end_node'])
node = nodeLatLon(final, ['old_bus', 'new_bus'])       
final = nodeLatLon(final, ['old_bus', 'new_bus'])

#%%
province_map = gpd.read_file(f'{main_path}/Maps/{province}Map.shp')
crs = {'init':'EPSG:4326'}
mapNodes = mapPoints(node)
mapMainNodes = mapPoints(main)
mainLines = mapLines(final)
allLines = mapLines(lines)

#%%
fig, ax = plt.subplots(figsize = (150,150))
province_map.to_crs(epsg = 4326).plot(ax=ax, color = 'gray')
mapNodes.plot(ax=ax, color = 'black', markersize = 50) #Nodes
mapMainNodes.plot(ax=ax, color = 'red', markersize = 100) #Main Nodes

if map_mode == 'Main':
    mainLines.plot(ax=ax, column = 'new_bus', cmap = 'tab20') #Lines from nodes to main nodes
elif map_mode == 'All':
    allLines.plot(ax=ax, color = 'black') #All lines
elif map_mode == 'AlgoCheck':
    algoCheck(checkNode, oldNode, ax)

if name_nodes == 'Main':
    # Name main nodes
    for x, y, label in zip(main['lon1'], main['lat1'], main['node']):
        ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points", fontsize = 20)
elif name_nodes == 'All':
    # Name all nodes
    for x, y, label in zip(final['lon1'], final['lat1'], final['old_bus']):
        ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points", fontsize = 20)
    
plt.savefig(f'{main_path}/Results/{province}_mapped_{map_mode}_{name_nodes}')
