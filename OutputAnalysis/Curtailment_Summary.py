#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 18:25:22 2022

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
 
#removing everything except wind data and dates
columns = available.columns[~available.columns.str.contains('Wind')]
columns = columns.drop(['date'])
available.drop(columns.astype(str), axis = 1, inplace = True)
available['date'] = available['date'] + ':00'

available.reset_index(drop = True, inplace = True)

i=0

for x in available['date']:
    available['date'].iloc[i] = datetime.datetime.strptime(available['date'].iloc[i] , '%m/%d/%Y %X')
    i= i+1



#same process for UC
uc_Results = files[files['name'].str.contains('UC_Results')]
uc_Results = uc_Results.rename({'name':'date'}, axis=1)
uc_Results = uc_Results.sort_values(by=['date'])

used = pd.DataFrame()

for file in uc_Results['date']:
    temp = pd.read_csv(path + '/' + file, header = 14)
    temp = temp.drop(temp.index[0:15], axis= 0)
    temp = temp.drop(temp.index[720:], axis= 0)
    tempdate = temp.pop('name')
    temp = temp.astype(float)
    temp = pd.concat([tempdate, temp], axis = 1)
    used = pd.concat([used, temp], axis = 0)
 
#removing everything except wind data and dates
columns = used.columns[~used.columns.str.contains('Wind')]
columns = columns.drop(['name']) 
used.drop(columns.astype(str), axis = 1, inplace = True)
used.reset_index(drop = True, inplace = True)

i = 0

for x in used['name']:
    used['name'].iloc[i] = datetime.datetime.strptime(used['name'].iloc[i] , '%Y-%m-%d %X')
    i= i+1

used = used.loc[used['name'].isin(available['date'])]
used = used.sort_values(by=['name'])
used.reset_index(drop = True, inplace = True)
used = used.rename({'name':'date'}, axis=1)
used.set_index(used['date'], inplace=True)

available = available.loc[available['date'].isin(used['date'])]
available = available.sort_values(by=['date'])
available.set_index(available['date'], inplace = True)


result = available.subtract(used, axis=0)
result.set_index(used['date'], inplace= True)
result = result.round(0)
result = result.replace({0:np.nan})
result = result.drop(columns=['date'])

totals = result.sum(0)
totals = totals[totals!=0]
yearMax = pd.Series([totals.sum(), totals.idxmax()], ['Year Total', 'Year Max'])
totals = totals.append(yearMax)
totals.rename('Total Curtailment [MW]', inplace=True)

result.insert(0, 'Hourly Max', result.idxmax(axis='columns', skipna=True))
result.insert(0, 'Hourly Totals [MW]', result.sum(1))




with pd.ExcelWriter('curtailment_results.xlsx') as path:
    available.to_excel(path, sheet_name= 'available')
    used.to_excel(path, sheet_name= 'used')
    result.to_excel(path, sheet_name='result')
    totals.to_excel(path, sheet_name='Summary')
