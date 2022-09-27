#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 16:29:49 2022

@author: nathan
"""
import pandas as pd
import geopandas as gpd

#import list of grid cells

#import list of demand centers
#create dataframe of points

#iterate through grid cells (Check which list is shorter, points or cells)
    #for each grid cell point, create a polygon with x degree lat and x degree lon
    #iterate through demand points
        #gridcell.contains(point)
        #update total population to that gridcell dataframe
        #maybe add name of point to gridcell as well
        
#save list of gridcells to excel with populations