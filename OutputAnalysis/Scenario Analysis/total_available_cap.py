#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 19:12:52 2022

@author: nathan
"""

import pandas as pd

import os
import datetime

def main(path_results, path_inputs, scenario, use_storage):
    #reading and storing names of relevant files
    files = pd.DataFrame(os.listdir(path_results), columns=['name'])
    
    available_VRE = files[files['name'].str.contains('Available_VRE_generation')]
    available_VRE = available_VRE.sort_values(by=['name'])
    
    #Read the available_VRE data spreadsheets
    available = pd.DataFrame()
    
    for file in available_VRE['name']:
         temp = pd.read_csv(f'{path_results}/{file}')
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
    
    #path to model inputs spreadsheet
    path = f'{path_inputs}/model inputs - {scenario}.xlsx'
    
    non_vre = pd.read_excel(path, sheet_name='non-vre plants', usecols=('name', 'bus', '[MW]'))
    non_vre['name'] = non_vre['name'].str.split('_', expand=True)[0]
    
    storage = pd.read_excel(path, sheet_name='storage', usecols=('kind', 'bus', '[MW]'))
    storage.rename(columns = {'kind':'name'}, inplace=True)
    storage = storage[['bus', 'name', '[MW]']]
    #remove this line if not wanted
    non_vre = non_vre.append(storage, ignore_index=True)
    
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
    sumtotal = pd.DataFrame(summary.groupby(['bus'])['[MW]'].sum())
    #add the storage in here if not wanted in total value, need to groupby again after append
    sumtotal.insert(0, 'name', 'total')
    sumtotal = sumtotal.reset_index(level=0)
    summary = summary.append(sumtotal, ignore_index=True)
    summary = summary.groupby(['bus', 'name'])['[MW]'].sum()
    
    
    #move line storage append here if not wanted in the yearly totals
    available = available.T
    available = available.reset_index(level=0)
    available.insert(0, 'bus', available['index'])
    available = available.replace({'bus': vreDict['bus']})
    available['index'] = available['index'].str.split('_', expand=True)[0]
    available.rename(columns={'index':'name'}, inplace=True)
    
    columns = list(available.columns.values)
    
    temp = pd.concat([non_vre['[MW]']] * (len(columns) - 2), axis=1)
    non_vre.drop(['[MW]'], inplace=True, axis=1)
    temp2 = non_vre.pop('name')
    non_vre.insert(1,'name', temp2)
    temp = pd.concat([non_vre, temp], axis=1)
    
    
    temp.set_axis(columns, inplace=True, axis=1)
    available = available.append(temp, ignore_index=True)
    
    hourlytotal = available.groupby(['bus']).sum()
    hourlytotal.insert(0, 'name', 'total')
    hourlytotal = hourlytotal.reset_index(level=0)
    
    available = available.append(hourlytotal, ignore_index=True)
    
    hourlysum = available.groupby(['bus', 'name']).sum().T
    
    
    
    #saving to excel
    with pd.ExcelWriter(f'{path_results}/{scenario}_available_capacity.xlsx') as path:
        summary.to_excel(path, sheet_name= 'summary')
        hourlysum.to_excel(path, sheet_name= 'hourly_sum')
        if use_storage:
            storagesum = storage.groupby(['bus', 'name']).sum()
            storagesum.to_excel(path, sheet_name= 'storage sum')
        
if __name__ == "__main__":
    main()