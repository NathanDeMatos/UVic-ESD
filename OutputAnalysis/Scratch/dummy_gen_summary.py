#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 12:54:51 2022

@author: nathan
"""

import pandas as pd
import os
import datetime

#Threshold for dummy generator usage
threshold = 5000

#load all relevant files from current directory
path = os.getcwd()
files = pd.DataFrame(os.listdir(path), columns=['name'])
uc_Results = files[files['name'].str.contains('UC_Results')]
uc_Results = uc_Results.rename({'name':'date'}, axis=1)
uc_Results = uc_Results.sort_values(by=['date'])

used = pd.DataFrame()

#Concatinate all the UC data into one dataframe
for file in uc_Results['date']:
    temp = pd.read_csv(path + '/' + file, header = 14)
    temp = temp.drop(temp.index[0:15], axis= 0)
    temp = temp.drop(temp.index[720:], axis= 0)
    tempdate = temp.pop('name')
    temp = temp.astype(float)
    temp = pd.concat([tempdate, temp], axis = 1)
    used = pd.concat([used, temp], axis = 0)

#removing everything except dummy gens
usedDummy = used
columns = usedDummy.columns[~usedDummy.columns.str.contains('NG_CC')]
columns = columns.drop(['name']) 
usedDummy.drop(columns.astype(str), axis = 1, inplace = True)
usedDummy.reset_index(drop = True, inplace = True)

#changing the format of the date-time values
i = 0
for x in usedDummy['name']:
    usedDummy['name'].iloc[i] = datetime.datetime.strptime(usedDummy['name'].iloc[i] , '%Y-%m-%d %X')
    i= i+1

usedDummy = usedDummy.sort_values(by=['name'])
usedDummy.reset_index(drop = True, inplace = True)
usedDummy = usedDummy.rename({'name':'date'}, axis=1)
usedDummy.set_index(usedDummy['date'], inplace=True)
usedDummy.drop('date', inplace=True,axis = 1)


with pd.ExcelWriter('dummy_gens.xlsx') as writer:
    for col in usedDummy.columns:
        temp = pd.DataFrame(usedDummy[col])
        temp = temp[temp[col] > 0]
        totalHours = len(temp.index)
        totalCap = temp.sum()
        temp = temp[temp[col] >= threshold]
        hoursAbove = len(temp.index)
        temp[col] = temp[col] - threshold
        temp = temp.round(1)
        stats = {'Hours On':totalHours, 'Hours Above': hoursAbove, 'Yearly Generation':totalCap}
        
        tempData = pd.DataFrame.from_dict(stats)
        temp = pd.concat([tempData, temp])
        temp.to_excel(writer, sheet_name = col.split('_')[2])
