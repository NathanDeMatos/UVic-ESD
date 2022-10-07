"""


@author: Noah Leverton
"""
from re import I, T
from tkinter import W
import pandas as pd
from pathlib import Path

# Setting paths to folders
model_inputs = Path().cwd() / "model_inputs" 
demand_real_forecasted = Path().cwd() / "demand_real_forecasted"
coders_path = Path().cwd() / "coders_data_inventories"

copper_scenario = 2410 
year = 2050 # Year of results


def base_capacity(province):

    # Importing capacities for each node
    non_vre = pd.read_excel(model_inputs / f"model inputs - {province}_{year}.xlsx",
                            sheet_name="non-vre plants",
                            usecols=['bus', '[MW]'])

    vre = pd.read_excel(model_inputs / f"model inputs - {province}_{year}.xlsx",
                        sheet_name="vre plants",
                        usecols=['bus', '[MW]'])


    if province == "CA":

        real_or_fc = "Zonal_Demand_Real"

    else:

        real_or_fc = "Zonal_Demand_Forecasted"

    demand = pd.read_excel(demand_real_forecasted / f"{province}_{year}_2.5x_Demand_Real_Forecasted.xlsx", 
                           sheet_name=real_or_fc,
                           usecols=(lambda x: x not in ['date', 'Total']))

    bus_region_mapping = pd.read_excel(model_inputs / f"model inputs - {province}_{year}.xlsx", 
                                       sheet_name="demand centres",
                                       index_col = [4, 0, 2])
    
    # bus_region_index = bus_region_mapping.index

    # Get max demands by population division
    max_demands = demand.max(axis = 0)
    max_demands.index.name = 'region'
    max_demands.name = 'Max Demand'

    if province != "CA":


        # Split division demands into smaller loads
        load_demands = max_demands*bus_region_mapping['frac pop']
        load_demands = load_demands.reset_index()

        # Aggregate into demands on buses
        bus_max_demands = load_demands.groupby('bus').sum()[0]
        bus_max_demands.name = 'Max Demand'

    else:

        bus_max_demands = max_demands.copy()

    # Aggregate vre/non-vre generation capacity
    bus_capacity = pd.concat([vre, non_vre]).groupby('bus').sum()['[MW]']

    # Mark other buses as 0 capacity
    # buses_without_capacity = set(list(bus_max_demands.index.values)).difference(set(bus_capacity.index.values))
    bus_capacity = bus_capacity.reindex(bus_max_demands.index, fill_value=0)


    bus_capacity.name = 'Total Capacity'

    total_on_buses = bus_capacity.copy()

    return total_on_buses, bus_max_demands

def node_connections(province):

    # Minimum distance paths between nodes
    nodes_map = pd.read_csv(Path().cwd() / f"node_connections_{province}.csv",
                            index_col=0)

    # Short and long CODERS node names
    mapping_df = pd.read_excel(coders_path / f"210818-{province}-DataInventory.xlsx",
                            sheet_name="Nodes",
                            header=1,
                            usecols=["Node Code", "Node Name"]).dropna()

    node_codes = mapping_df["Node Code"].values
    coders_names = mapping_df["Node Name"].values

    # Nodes as represented in SILVER
    silver_nodes = pd.read_excel(model_inputs / f"model inputs - {province}.xlsx", "demand centres")['bus'].drop_duplicates().values

    # Create mapping from short node codes to full names
    code_to_coders_name = dict(zip(node_codes, coders_names))

    # Change connection nodes names to full CODERS names
    full_name_connections = nodes_map.rename(columns=code_to_coders_name, index=code_to_coders_name)
    coders_name_to_silver = dict.fromkeys(coders_names)

    if province == "AB":

        for x in coders_name_to_silver:

            coders_name_to_silver[x] = x.upper().replace(" ", "")

        # Add missed nodes
        coders_name_to_silver["Castle Downs 557S"] = "CASTLEDOWNS"
        coders_name_to_silver["Dome 665S"] = "DOME"
        coders_name_to_silver["Genesee 330P"] = "GENESEE330"
        coders_name_to_silver["Newell 2075S"] = "NEWELL2075S89S"
        coders_name_to_silver["Petrolia 816S"] = "PETROLIA"

    elif province == "BC":

        # Creating mapping between CODERS and SILVER node names
        for x in silver_nodes:

            coders_name_to_silver[x.partition(' - ')[2]] = x

        # Correct one node
        coders_name_to_silver["Kennedy"] = coders_name_to_silver.pop("Kennedy Capacitor Station")


    elif province == "MB":

        for x in coders_name_to_silver:

            coders_name_to_silver[x] = x.upper().strip()
       
        coders_name_to_silver["Kelsey TS"] = "KELSEY TERMINAL"

    elif province == "SK":

        for x in coders_name_to_silver:

            coders_name_to_silver[x] = x
        
        coders_name_to_silver["Regina South"] = "Regina"
    
    elif province == "ON":
        
        # Add missed nodes
        coders_name_to_silver["Ashfield SWS"] = "Ashfield SS"
        coders_name_to_silver["Bowmanville SWS"] = "Bowmanville SS"
        coders_name_to_silver["Bruce B SWS"] = "Bruce B SS"
        coders_name_to_silver["Evergreen SWS"] = "Evergreen SS"
        coders_name_to_silver["K2 Wind GS"] = "K2 Wind 500 CGS"
        coders_name_to_silver["Milton SWS"] = "Milton SS"
        coders_name_to_silver["Napanee GS"] = "Napanee CSS"
        coders_name_to_silver["Nobel SWS"] = "Nobel SS"
        coders_name_to_silver["Parkhill TS"] = "Parkhill CTS"
        
    coders_name_to_silver = {x:y for x,y in coders_name_to_silver.items() if y in silver_nodes}

    silver_connections = full_name_connections.rename(columns=coders_name_to_silver, index=coders_name_to_silver
                                                      ).loc[silver_nodes, silver_nodes]

    # Confirm that nodes were not lost
    assert len(silver_nodes) == len(silver_connections)
    
    return silver_connections

def transmission(connections, capacities, n):

    new_capacities = pd.Series(index=capacities.index, dtype='float64', name = capacities.name)

    for bus in capacities.index:

        # Create list of nodes connecting to this bus in a maximum of n steps
        # to_add = set(list(connections.loc[(connections[bus]>0) & 
        #                                   (connections[bus]<=n)][bus].index.values)).intersection(set(list(capacities.index.values)))
        
        # to_add = list(to_add)

        to_add = connections.loc[(connections[bus]>0) & (connections[bus]<=n)][bus].index.values

        if len(to_add)>0:
            
            # Add down/upstream node capacities to this bus
            new_capacities[bus] = capacities[bus] + capacities[to_add].sum()
        
        else:

            new_capacities[bus] = capacities[bus]

    return new_capacities

def main():

    # provinces = ["AB", "BC", "MB", "SK", "ON"]

    # base_capacities = dict.fromkeys(provinces)
    # silver_connections = dict.fromkeys(provinces)

    # for province in provinces:

    #     pass

    province = "ON"

    if province == "CA":

        # demand = pd.read_excel(demand_real_forecasted / f"{province}_{year}_Demand_Real_Forecasted.xlsx", 
        #                         sheet_name="Zonal_Demand_Forecasted",
        #                         usecols=(lambda x: x not in ['date', 'Total']))
        
        # max_demands = demand.max(axis = 0)

        # capacities = 

        capacities_CA, max_demands_CA = base_capacity(province)

        pass

    else:

        capacities, max_demands = base_capacity(province)
        silver_connections = node_connections(province)

        for connection_distance in range(1,4):

            new_capacities = transmission(silver_connections, capacities, connection_distance)
                
            analysis = pd.DataFrame({"Total Capacity": new_capacities,
                                     "Max Demand": max_demands,
                                     "Capacity/Demand": new_capacities/max_demands}
                                    ).fillna(0).sort_values("Capacity/Demand", ascending=False)

            analysis.to_csv(Path().cwd() / "results" / f"analysis_scenario_{copper_scenario}_{province}_{year}_max_distance_{connection_distance}.csv")
        

if __name__ == "__main__":
    main()