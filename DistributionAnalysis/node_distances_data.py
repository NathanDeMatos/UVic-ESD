#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 15:01:23 2022

@author: nathan
"""

#Imports data from API and formats to excel

import pandas as pd
import os
import requests
import json
import re
from pathlib import Path


province = 'ON' #set the desired province
x = requests.get('http://206.12.95.90/transmission_lines?province=' + province)

path = "/home/nathan/UVic-ESD/Dijkstra/Results/"

suffix = "temp.json"
path1 =f"{path[0].upper()}{path[1:]}{province}{suffix}"
suffix = "formatted.json"
path2 = f"{path[0].upper()}{path[1:]}{province}{suffix}"
suffix = "data.xlsx"
path3 = f"{path[0].upper()}{path[1:]}{province}{suffix}"
with open(path1, "w") as output:
    for variable in x.json():
        json.dump(variable,output)

#the json.dump outputs the data into a json file with no commas "}{" the few lines
#code below change it to "},{" which makes it readable by panada
with open(path1, 'r') as input, open(path2, 'w') as output:
    for line in input:
        line = re.sub('}{', '},{', line)
        output.write('    '+line)
os.remove(path1)

df_json = pd.read_json(path2, lines=True)
df_json.to_excel(path3)

os.remove(path2)

transmission = pd.read_excel(path3)
node_distances_data = Path().cwd() / "node_distances_data"
transmission.to_csv(node_distances_data / f"Transmission-{province}.csv")