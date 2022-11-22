#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 20:00:46 2022

@author: nathan
"""

import pandas as pd
import numpy as np
import datetime
import os

def main(path_results, path_inputs, scenario):
    files = pd.DataFrame(os.listdir(path_results), columns=['name'])
    
    lineFlow = files[files['name'].str.contains('Line_Flow')]
    
    #Read the available_VRE data spreadsheets
    flows = pd.DataFrame()
    
    
    for file in lineFlow['name']:
         temp = pd.read_csv(f'{path_results}/{file}')
         
         startDate =  datetime.datetime.strptime(file.split('_')[2], '%Y-%m-%d')
         endDate = datetime.datetime.strptime(file.split('_')[3].split('.')[0], '%Y-%m-%d')
         endDate -= datetime.timedelta(hours = 1)
         tempDates = pd.date_range(startDate, endDate, freq='H')
         
         lines = temp['from'] + ' to ' + temp['to']
         
         temp = temp.drop(['to', 'from'], axis=1)
         temp = temp.astype(float)
         temp = temp.abs()
         temp = temp.T
         
         temp = temp.set_index(tempDates)   
         
         flows = pd.concat([flows, temp], axis = 0)
    
    flows.sort_index(inplace=True)
    flows = flows.set_axis(lines, axis=1)
    
    
    path = f'{path_inputs}/model inputs - {scenario}.xlsx'
    pmax = pd.read_excel(path, sheet_name = 'existing transmission')
    lines = pmax['from bus'] + ' to ' + pmax['to bus']
    pmax = pmax['pmax'].to_frame()
    pmax = pmax.T
    pmax = pd.concat([pmax] * len(flows))
    pmax = pmax.set_axis(lines, axis=1)
    pmax = pmax.set_index(flows.index)
    
    result = pmax.subtract(flows, axis=1)
    result = result.round(0)
    result = result.replace({0:np.nan})
    
    totals = pd.Series(result.sum(0), name='Surplus')
    
    
    #saves results as excel spreadsheet
    with pd.ExcelWriter(f'{path_results}/{scenario}_flow_results.xlsx') as path:
        flows.to_excel(path, sheet_name= 'flows')
        pmax.to_excel(path, sheet_name= 'pmax')
        result.to_excel(path, sheet_name = 'results')
        totals.to_excel(path, sheet_name='surplus')
        
if __name__ == "__main__":
    main()