#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 18:45:15 2022

@author: nathan
"""

import pandas as pd
import os

#Enter the path to the demand file
def main(path_result, path_input, scenario):
    path = f'{path_input}/{scenario}_Demand_Real_Forecasted.xlsx'

    demand = pd.read_excel(path, sheet_name='Zonal_Demand_Real')
    demand = demand.set_index(demand['date'])
    demand = demand.drop(['date'], axis=1)
    demand = demand.astype(float)
    
    maxDemand = demand.max(0)
    maxDemandDict = maxDemand.to_dict()
    
    maxHour = demand.idxmax(0)
    maxHourDict = maxHour.to_dict()
    
    results = pd.concat([maxHour, maxDemand],axis=1)
    results = results.set_axis(['Max Hour', 'Max Demand'], axis=1)
    
    with pd.ExcelWriter(f'{path_result}/{scenario}_demand_results.xlsx') as path:
        results.to_excel(path, sheet_name= 'results')

if __name__ == "__main__":
    main()