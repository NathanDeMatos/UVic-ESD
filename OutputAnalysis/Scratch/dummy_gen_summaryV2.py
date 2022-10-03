#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 14:36:29 2022

@author: nathan
"""

import pandas as pd
import os
import datetime

#Threshold for dummy generation usage
threshold = 5000

#Read relevant files from current directory
path = os.getcwd()
files = pd.DataFrame(os.listdir(path), columns=['name'])
uc_Results = files[files['name'].str.contains('UC_Results')]
uc_Results = uc_Results.rename({'name':'date'}, axis=1)
uc_Results = uc_Results.sort_values(by=['date'])

used = pd.DataFrame()

#Concatinate all UC files together into single dataframe
for file in uc_Results['date']:
    #Discarding irrelevant rows of csv
    temp = pd.read_csv(path + '/' + file, header = 1)
    temp = temp.drop(temp.index[0:12], axis= 0)
    pmax = temp.loc[14] #Storing pmax values
    temp = temp.drop(temp.index[1:16], axis=0)
    temp = temp.drop(temp.index[720:], axis= 0)
    
    #Getting names of generators
    tempT = temp.T
    names = tempT.pop(12)
    temp = tempT.T
    
    #Changing values to float, temporarily removing dates
    tempdate = temp.pop('bus')    
    temp = temp.astype(float)
    
    #Merging dates back in, concating all files together
    temp = pd.concat([tempdate, temp], axis = 1)
    used = pd.concat([used, temp], axis = 0)

#Reformatting date-time for consistency between files
i = 0
for x in used['bus']:
    used['bus'].iloc[i] = datetime.datetime.strptime(used['bus'].iloc[i] , '%Y-%m-%d %X')
    i= i+1

#Sorting entries by date-time
used = used.sort_values(by=['bus'])

#Inserting pmax values
temp = pd.DataFrame(pmax)
used = pd.concat([temp.T, used], axis = 0)

#Inserting names
temp = pd.DataFrame(names)
used = pd.concat([temp.T, used], axis = 0)


#Reading the line flows data (requires flow_results.xlsx to be in folder)
flows = pd.read_excel(path+'/flow_results.xlsx', index_col=0)
flows = flows.round(2)

#Manually entered list of BA
provinces = {'ON.a', 'ON.b', 'NB.a', 'BC.a', 'AB.a', 'SK.a', 'QC.a', 'QC.b', 'NS.a', 'PE.a', 'MB.a', 'NL.a', 'NL.b'}

#This part is so messy
with pd.ExcelWriter('dummy_gens.xlsx') as writer:
    #Iterate through each balancing area
    for prov in provinces:
        usedDummy = pd.DataFrame(used)
        
        #Discarding all generators not within BA
        columns = usedDummy.columns[~usedDummy.columns.str.contains(prov)]
        columns = columns.drop(['bus'])
        usedDummy.drop(columns.astype(str), axis = 1, inplace = True)
        usedDummy.reset_index(drop = True, inplace = True)
        
        #Discarding all line flows not within BA
        tempflows = pd.DataFrame(flows)
        columns = tempflows.columns[~tempflows.columns.str.contains(prov)]
        tempflows.drop(columns.astype(str), axis = 1, inplace = True)
        
        #Discarding everything except dummy gen, wind, storage
        columns = usedDummy.columns[~usedDummy.loc[0].str.contains('NG_CC|Wind|batteries|PHS')]
        columns = columns.drop(['bus'])
        usedDummy.drop(columns.astype(str), axis = 1, inplace = True)
        usedDummy.reset_index(drop = True, inplace = True)
        
        #Formatting dataframe
        usedDummy.reset_index(drop = True, inplace = True)
        usedDummy = usedDummy.rename({'bus':'date'}, axis=1)
        usedDummy.set_index(usedDummy['date'], inplace=True)
        usedDummy.drop('date', inplace=True,axis = 1)
        usedDummy.rename(usedDummy.loc['name'], inplace=True, axis=1)
        
        #removing pmax and names temporarily
        temp = usedDummy.T
        temp.pop('name')
        pmax = temp.pop('pmax')
        usedDummy = temp.T
        
        #manipulating generation data
        usedDummy = usedDummy[usedDummy.iloc[:,0] > 0] #removing every hour where dummy gens weren't on
        totalHours = len(usedDummy.index) #total hours dummy gens were active
        totalCap = int(usedDummy.iloc[:,0].sum()) #total amount generated by dummy
        usedDummy = usedDummy[usedDummy.iloc[:,0] >= threshold] #remove every hour where dummy was less than threshold
        hoursAbove = len(usedDummy.index) #hours dummy was above threshold
        usedDummy = usedDummy.round(1)
        stats = {'Hours On':[totalHours], 'Hours Above': [hoursAbove], 'Yearly Generation':[totalCap]}
        
        #Calculating capacity factors for wind gens
        capFact = pd.DataFrame(usedDummy)
        capFact = capFact.astype(float)
        tempData = pd.DataFrame.from_dict(stats)
        temppmax = pd.DataFrame(pmax)
        temppmax = temppmax.astype(float)
        capFact = capFact.T
        capFact = capFact.divide(temppmax['pmax'], axis=0).T
        capFact = capFact.add_suffix('_CF')
        capFact = capFact.round(2)
        
        #Calculate average hourly capacity factor
        averageCF = pd.DataFrame(capFact.mean(axis=1), columns = ['Average CF'])
        averageCF = averageCF.round(2)
        
        #merging cap factors, stats and pmax to data
        usedDummy = pd.concat([temppmax.T, usedDummy])
        usedDummy = pd.concat([tempData, usedDummy])
        usedDummy = pd.concat([usedDummy, averageCF], axis=1)
        usedDummy = pd.concat([usedDummy, capFact], axis=1)
        usedDummy = usedDummy.join(tempflows,how='left')
        
        #saving to excel
        usedDummy.to_excel(writer, sheet_name = prov)