#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

model_inputs_in = Path().cwd() / "model_inputs"
coders_path = Path().cwd() / "coders_data_inventories"

def node_formatter(province):

    # Matching node data from CODERS with format from SILVER

    # data = Path().cwd() / "files_needed_for_tool"    

    nodes_format = pd.read_excel(model_inputs_in / f"model inputs - {province}.xlsx", "demand centres")['bus'].drop_duplicates()
    nodes_coders = pd.read_excel(coders_path / f'210818-{province}-DataInventory.xlsx', sheet_name='Nodes', header = 1).dropna(how='all')[['Node Name', 'Node Code']]

    if province == 'AB':

        # Reformatting data
        nodes_coders['Node Name'] = nodes_coders['Node Name'].str.upper()
        nodes_coders['Node Name'] = nodes_coders['Node Name'].str.replace(' ', "")
        nodes = pd.merge(nodes_coders, nodes_format, left_on='Node Name', right_on='bus')
        nodes = pd.concat([nodes, nodes_coders.loc[nodes_coders['Node Name'].isin(['CASTLEDOWNS557S','DOME665S', 'GENESEE330P', 'NEWELL2075S', 'PETROLIA816S'])]])

        # Renaming to match demand centres
        nodes.loc[nodes['Node Name'] == 'CASTLEDOWNS557S', 'Node Name'] = 'CASTLEDOWNS'
        nodes.loc[nodes['Node Name'] == 'DOME665S', 'Node Name'] = 'DOME'
        nodes.loc[nodes['Node Name'] == 'GENESEE330P', 'Node Name'] = 'GENESEE330'
        nodes.loc[nodes['Node Name'] == 'NEWELL2075S', 'Node Name'] = 'NEWELL2075S89S'
        nodes.loc[nodes['Node Name'] == 'PETROLIA816S', 'Node Name'] = 'PETROLIA'

        nodes['bus'] = nodes['Node Name']
        nodes = nodes.drop('Node Name', axis=1).reset_index(drop=True)


    elif province == 'BC':
       # Add acronyms to beginnings of CODERS names
        for index, value in nodes_format.iteritems():

            remove_acronym = value.partition(' - ')[2]

            nodes_coders.loc[nodes_coders['Node Name'] == remove_acronym, 'Node Name'] = value

        nodes = pd.merge(nodes_coders, nodes_format, left_on='Node Name', right_on='bus')
        nodes = pd.concat([nodes, nodes_coders.loc[nodes_coders['Node Name'].isin(['Kennedy'])]])

        nodes.loc[nodes['Node Name']=='Kennedy', 'bus'] = 'KDY - Kennedy Capacitor Station'
        nodes = nodes.drop('Node Name', axis=1).reset_index(drop=True).sort_index()

    elif province == 'MB':

        nodes_format = nodes_format.str.strip()
        nodes_coders['Node Name'] = nodes_coders['Node Name'].str.upper()
        nodes_coders['Node Name'] = nodes_coders['Node Name'].str.strip() 
        nodes = pd.merge(nodes_coders, nodes_format, left_on='Node Name', right_on='bus')
        nodes = pd.concat([nodes, nodes_coders.loc[nodes_coders['Node Name'] == 'KELSEY TS']])
        
        nodes.loc[nodes['Node Name'] == 'KELSEY TS', 'Node Name'] = 'KELSEY TERMINAL'
        nodes['bus'] = nodes['Node Name']
        nodes = nodes.drop('Node Name', axis=1).reset_index(drop=True)

    # Saskatchewan nodes are already in a matching format
    elif province == 'SK':

        nodes = pd.merge(nodes_coders, nodes_format, left_on='Node Name', right_on='bus').drop('Node Name', axis = 1).reset_index(drop=True)
        nodes = pd.concat([nodes, nodes_coders.loc[nodes_coders['Node Name'] == 'Regina South']])
        nodes['bus'] = nodes['Node Name']
        nodes = nodes.drop('Node Name', axis=1).reset_index(drop=True)
        pass

    
    if len(nodes) != len(nodes_format):
        print("Some nodes were lost: \n")
        # print(nodes['bus'].compare(nodes_format))
    
    return nodes

nodes_map = pd.read_csv(Path().cwd() / "node_connections_BC.csv",
                        index_col=0)

mapping_df = pd.read_excel(coders_path / "210818-BC-DataInventory.xlsx",
                           sheet_name="Nodes",
                           header=1,
                           usecols=["Node Code", "Node Name"]).dropna()

node_codes = mapping_df["Node Code"].values
coders_names = mapping_df["Node Name"].values
silver_nodes = pd.read_excel(model_inputs_in / "model inputs - BC.xlsx", "demand centres")['bus'].drop_duplicates().values

code_to_coders_name = dict(zip(node_codes, coders_names))

# Change to full coders names
full_name_connections = nodes_map.rename(columns=code_to_coders_name, index=code_to_coders_name)
coders_name_to_silver = dict.fromkeys(coders_names)

for x in silver_nodes:

    coders_name_to_silver[x.partition(' - ')[2]] = x

coders_name_to_silver = {x:y for x,y in coders_name_to_silver.items() if y is not None}

# Correct one node
coders_name_to_silver["Kennedy"] = coders_name_to_silver.pop("Kennedy Capacitor Station")
silver_connections = full_name_connections.rename(columns=coders_name_to_silver, index=coders_name_to_silver).loc[silver_nodes, silver_nodes]

# Check that nodes were not lost
len(silver_nodes) == len(silver_connections)