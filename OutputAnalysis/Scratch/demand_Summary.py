#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 18:45:15 2022

@author: nathan
"""

import pandas as pd
import os

#Enter the path to the demand file
path = os.getcwd() + '/CA_2050_2410_Demand_Real_Forecasted.xlsx'

demand = pd.read_excel(path, sheet_name='Zonal_Demand_Real')
demand.set_index(demand['date'], inplace=True)
demand = demand.drop(['date'], axis=1)
demand = demand.astype(float)

maxDemand = demand.max(0)
maxDemand = maxDemand.astype(str)
maxDemandDict = maxDemand.to_dict()

maxHour = demand.idxmax(0)
maxHour = maxHour.astype(str)
maxHourDict = maxHour.to_dict()

results = pd.concat([maxHour, maxDemand],axis=1)
results.set_axis(['Max Hour', 'Max Demand'], axis=1, inplace=True)

with pd.ExcelWriter('demand_results.xlsx') as path:
    results.to_excel(path, sheet_name= 'results')
