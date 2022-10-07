# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 14:51:32 2022

@author: Nathan de Matos
"""
from pathlib import Path
import collections 
import pandas as pd
import heapq


# In[3]:


#Imports data from API and formats to excel

# =============================================================================
# province = 'MB' #set the desired province
# x = requests.get('http://206.12.95.90/transmission_lines?province=' + province)
# 
# path = "/home/nathan/UVic-ESD/Dijkstra/Results/"
# 
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


# In[4]:


#Creates dataframes
provinces = ["AB", "MB", "SK"]
province = provinces[2]

node_distances_data = Path().cwd() / "node_distances_data"
raw_data = pd.read_csv(node_distances_data / f"Transmission-{province}.csv") #temporarily reading directly from file
transmission_data = pd.DataFrame([], columns=["from_bus", "to_bus", "distance"])
transmission_data['from_bus'] = raw_data['starting_node_code']
transmission_data['to_bus'] = raw_data['ending_node_code']
transmission_data['distance'] = raw_data['line_segment_length_km'] - raw_data['line_segment_length_km'] + 1

main_nodes = set(transmission_data['to_bus']).union(set(transmission_data['from_bus']))
# In[5]:


#Running Dijkstra

graph = collections.defaultdict(dict) #dictionary of edges and vertices (graph)

for index,row in transmission_data.iterrows(): #iterate through rows of dataframe
    graph[row['from_bus']][row['to_bus']] = row['distance'] #set edge with to node, from node and distance
    graph[row['to_bus']][row['from_bus']] = row['distance'] #set same edge in opposite direction (bidirectional)

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

# In[6]:

#Formatting output and saving to excel
result = pd.DataFrame.from_dict(distances)
result.to_csv(f"node_connections_{province}.csv")