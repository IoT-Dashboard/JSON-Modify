import json
import os
from helper import *

# open json file
original_file_name = 'flows.json'
with open(original_file_name, 'r') as file:
    data = json.load(file)

mismatched_nodes = []

# check if ui nodes match station and single/multi station view
for node in data:
    if node['type'] == 'ui_template':
        station_number = extract_station_number(node['name'])
        
        if station_number is not None:
            ui_group = node['group']
            if node['name'][1] == 'M':
                check_group = get_group_id('multi', station_number + 1)
            else:
                check_group = get_group_id('single', station_number + 1)
            
            if ui_group != check_group:
                mismatched_nodes.append(node['name'])
                
print(mismatched_nodes)
        