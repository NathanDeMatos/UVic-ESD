#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 19:12:52 2022

@author: nathan
"""

import pandas as pd
import numpy as np
import os
import datetime

#reading and storing names of relevant files
path = '/home/nathan/UVic-ESD/OutputAnalysis/Scratch/Model Results'
files = pd.DataFrame(os.listdir(path), columns=['name'])

available_VRE = files[files['name'].str.contains('Available_VRE_generation')]
vailable_VRE = available_VRE.sort_values(by=['name'])

#Read the available_VRE data spreadsheets
available = pd.DataFrame()

for file in available_VRE['name']:
     temp = pd.read_csv(path + '/' + file)
     tempdate = temp.pop('date')
     temp = temp.astype(float)
     temp = pd.concat([tempdate, temp], axis = 1)
     available = pd.concat([available, temp], axis = 0)
 

available.drop(['Unnamed: 0'], axis = 1, inplace = True)
available['date'] = available['date'] + ':00'
available = available.sort_values(by=['date'])

#changing datatype of date values
i=0
for x in available['date']:
    available['date'].iloc[i] = datetime.datetime.strptime(available['date'].iloc[i] , '%m/%d/%Y %X')
    i= i+1

available.set_index(available['date'], inplace = True)
available.drop(['date'], inplace=True, axis=1)


path = '/home/nathan/UVic-ESD/OutputAnalysis/Scratch/Model Inputs/model inputs - CA_2050_2410 - Original.xlsx'

non_vre = pd.read_excel(path, sheet_name='non-vre plants', usecols=('name', 'bus', '[MW]'))
non_vre['name'] = non_vre['name'].str.split('_', expand=True)[0]


vre = pd.read_excel(path, sheet_name='vre plants', usecols=('name', 'bus'))
vre.set_index(vre['name'], inplace=True)
vre.drop(['name'], axis=1, inplace=True)
vreDict = vre.to_dict()
vre['[MW]'] = 0

for gen, bus in vre.iterrows():
    vre['[MW]'][gen] = available[gen].sum()

vre = vre.reset_index(level=0)
vre['name'] = vre['name'].str.split('_', expand=True)[0]

summary = vre.append(non_vre, ignore_index=True)
summary = summary.groupby(['bus', 'name'])['[MW]'].sum()


available = available.T
available = available.reset_index(level=0)
available.insert(0, 'bus', available['index'])
available = available.replace({'bus': vreDict['bus']})
available['index'] = available['index'].str.split('_', expand=True)[0]
hourlysum = available.groupby(['bus', 'index']).sum().T

#saving to excel
with pd.ExcelWriter('available_capacity.xlsx') as path:
    summary.to_excel(path, sheet_name= 'summary')
    hourlysum.to_excel(path, sheet_name= 'hourly_sum')