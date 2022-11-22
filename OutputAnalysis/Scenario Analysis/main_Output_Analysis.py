#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 14:45:26 2022

@author: nathan
"""

from pathlib import Path

import Curtailment_Summary
import demand_Summary
import dummy_gen_summaryV2
import Flows_Summary
import total_available_cap

scenario = 'Scratch'

dummy_gens = True
#Threshold for dummy generation usage
threshold_dummy_gen = 4000

storage = True

path = str((Path().resolve().parent).parent)
path = f'{path}/SILVER_Data'
path_user_inputs = f'{path}/user_inputs' # Demand_Real_Forecasted, model inputs
path_results = f'{path}/Model Results/{scenario}'

Curtailment_Summary.main(path_results, scenario)
demand_Summary.main(path_results, path_user_inputs, scenario)
Flows_Summary.main(path_results, path_user_inputs, scenario)
total_available_cap.main(path_results, path_user_inputs, scenario, storage)

if dummy_gens:
    dummy_gen_summaryV2.main(path_results, threshold_dummy_gen, scenario)