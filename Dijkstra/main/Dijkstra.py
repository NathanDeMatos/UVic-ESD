#!/usr/bin/env python
# coding: utf-8

# In[1]:


import collections 
import pandas as pd
import os
import requests
import json
import re
import heapq

#Imports data from API and formats to excel
province = 'BC' #set the desired province

node_voltage = {500} #the node voltage used to check which nodes to aggregate to
manual_nodes = {} #any nodes to be manually added as main nodes

# =============================================================================
# 
# path = os.getcwd()
# x = requests.get('http://206.12.95.90/transmission_lines?province=' + province)
# suffix = "temp.json"
# path1 =f"{path[0].upper()}{path[1:]}{province}{suffix}"
# suffix = "formatted.json"
# path2 = f"{path[0].upper()}{path[1:]}{province}{suffix}"
# suffix = "data.xlsx"
# path3 = f"{path[0].upper()}{path[1:]}{province}{suffix}"
# with open(path1, "w") as output:
#     for variable in x.json():
#         json.dump(variable,output)
# 
# #the json.dump outputs the data into a json file with no commas "}{" the few lines
# #code below change it to "},{" which makes it readable by panada
# with open(path1, 'r') as input, open(path2, 'w') as output:
#     for line in input:
#         line = re.sub('}{', '},{', line)
#         output.write('    '+line)
# os.remove(path1)
# 
# df_json = pd.read_json(path2, lines=True)
# df_json.to_excel(path3)
# 
# os.remove(path2)
# =============================================================================

#Creates dataframes
transmission_data = pd.read_csv('/home/nathan/UVic-ESD/Dijkstra/Data/Transmission-BC.csv', usecols=['starting_node_code', 'ending_node_code', 'line_segment_length_km', 'voltage_in_kv'])
transmission_data = transmission_data.loc[(transmission_data['starting_node_code'].str.contains(province)) | (transmission_data['ending_node_code'].str.contains(province))]

raw_node_data = pd.read_csv('/home/nathan/UVic-ESD/Dijkstra/Data/CODERS-Nodes.csv')

#removes all data except for desired province
raw_node_data = raw_node_data[raw_node_data['province'] == province]

#storing set of 'main nodes' to use as starting nodes
main_nodes = transmission_data[transmission_data['voltage_in_kv'].isin(node_voltage)] 
main_nodes = set(main_nodes['starting_node_code']).union(set(main_nodes['ending_node_code']))
main_nodes = main_nodes.union(manual_nodes)
main = pd.DataFrame(main_nodes, columns = ['node'])

#Running Dijkstra
graph = collections.defaultdict(dict) #dictionary of edges and vertices (graph)

for index,row in transmission_data.iterrows(): #iterate through rows of dataframe
    graph[row['starting_node_code']][row['ending_node_code']] = row['line_segment_length_km'] #set edge with to node, from node and distance
    graph[row['ending_node_code']][row['starting_node_code']] = row['line_segment_length_km'] #set same edge in opposite direction (bidirectional)

distances = {i:{ j: float("inf") for j in graph} for i in main_nodes} #dictionary of shortest distances from each main_node {main_node: {every_node:every_distance}}

for start_node in main_nodes:
    distances[start_node][start_node] = 0 #setting first node distance as 0
    min_dist = [(0,start_node)] #heap of shortest distances (distance, node)
    visited = set() #set of all visited nodes
    
    while min_dist: #while heap is not empty
            
        cur_dist, cur = heapq.heappop(min_dist) #pop smallest value from heap, store it's distance and node
       
        if cur in visited: continue #skip this loop if current node has been visited
        
        visited.add(cur) #add current node to set of visited nodes
            
        for neighbor in graph[cur]: #iterate through neighbors of current node
        
            if neighbor in visited: continue #skip if in set of visited nodes
            
            this_dist = cur_dist + graph[cur][neighbor] #calculate new distance = distance to neighbor + distance to current node
        
            if this_dist  < distances[start_node][neighbor]: #check which is smaller
                distances[start_node][neighbor] = this_dist #store if new distance is smaller
                heapq.heappush(min_dist, (this_dist, neighbor)) #push neighbor to heap

#Formatting output and saving to excel
result = pd.DataFrame.from_dict(distances)
new = {'new_bus' : result.idxmin(axis=1)}
final = pd.DataFrame(new)
final = final.rename(columns = {'index':'old_bus'})

with pd.ExcelWriter('Aggregated_nodes.xlsx') as writer:
    final.to_excel(writer, sheet_name = province)