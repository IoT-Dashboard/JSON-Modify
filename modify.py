import json
import os
from helper import *

# File setup for loading and saving JSON
original_file_name = 'flows.json'
base_new_file_name = 'new_flows'
counter = 1
new_file_name = f"{base_new_file_name}.json"
folder_path = 'Dashboard_Files/'

# File name for json with mqtt information
mqtt_file_name = "mqtt.json"

# Ensuring the output file name is unique by incrementing a counter if the file already exists
while os.path.exists(new_file_name):
    new_file_name = f"{base_new_file_name}_{counter}.json"
    counter += 1
file_path = folder_path + new_file_name

# Loading the original JSON data from file
with open(original_file_name, 'r') as file:
    data = json.load(file)

# Loading mqtt information from file
with open(mqtt_file_name, 'r') as file:
    mqtt_info = json.load(file)

# Obtain the MQTT in node topics from mqtt.json
event_manager = mqtt_info['EventManagerName']
tracking_manager = mqtt_info['TrackingManagerName']
stations = mqtt_info['Stations']

# Create a dictionary with all the mqtt topics
topics = []
for station in stations:
    event_base = f"{event_manager}/{station['LineName']}/{station['Name']}"
    tracking_base = f"{tracking_manager}/{station['LineName']}/{station['Name']}"
    station_topics = {
        'Bucket State': f"{tracking_base}/production/bucketstate",
        'Tracking': f"{tracking_base}/tracking",
        'Likely': f"{tracking_base}/production/likely",
        'Production': f"{tracking_base}/production",
        'System Events': f"{event_base}/systemevents",
        'Andon Events': f"{event_base}/andonevents",
        'name': station['Name']
    }
    topics.append(station_topics)
num_stations = len(stations)

indices_to_delete = set()
index = 0
subflow_indices = {}
subflows_to_delete = set()
IMN_y_positions = []

# Updating node topics and names in the JSON data
for node in data:
    node_type = node.get('type')
    node_name = node.get('name')
    
    if node_type == 'mqtt in':
        station_number = extract_station_number(node_name)
        
        if station_number is not None:
            if station_number < num_stations:
                station_topics = topics[station_number]
                for key in station_topics:
                    if key in node_name:
                        topic = station_topics[key]
                node['topic'] = topic
            else:
                attached_subflow = node['wires'][0][0]
                subflows_to_delete.add(attached_subflow)
                indices_to_delete.add(index)
                
        else:
            station_topics = topics[0]
            if 'Likely' in node['name']:
                node['topic'] = station_topics['Likely']
            elif 'Production' in node['name']:
                node['topic'] = station_topics['Production']
       
    elif node_type == 'ui_tab':
        station_number = extract_station_number(node_name)
        if station_number is not None:
            if station_number < num_stations:
                station_topics = topics[station_number]
                node['name'] = station_topics['name']
            else:
                indices_to_delete.add(index)
            
    elif node_type == 'switch':
        node['rules'] = node['rules'][0 : num_stations]
        
    elif node_type == 'ui_template':
        station_number = extract_station_number(node_name)
        if station_number is not None and station_number >= num_stations:
            indices_to_delete.add(index)
       
    elif node_type == 'ui_group':
        station_number = extract_station_number(node_name)
        if station_number is not None and station_number >= num_stations:
            indices_to_delete.add(index)
        elif node['name'] == 'Station':
            station_number = get_station_from_group(node['id'])
            if station_number > num_stations:
                indices_to_delete.add(index)
            
    elif node_type == 'ui_tab':
        station_number = extract_station_number(node_name)
        if station_number is not None and station_number >= num_stations:
            indices_to_delete.add(index)
    
    elif 'subflow' in node['type']:
        group_id = node['id']
        subflow_indices[group_id] = index
        
        # Keep dict of IMN subflows and their y position to know which to delete
        if '15111a9d6510dc85' in node['type']:
            id = node['id']
            IMN_y_positions.append({'index': index, 'y': node['y']})
    
    index += 1

# Determine which IMN flows to remove based on y position and number of stations
IMN_y_positions = sorted(IMN_y_positions, key=lambda d: d['y'])
for item in IMN_y_positions[num_stations:]:
    indices_to_delete.add(item['index'])

# Create a set with all the indices to delete
to_delete = indices_to_delete.union(subflows_to_delete)
for item in to_delete:
    if isinstance(item, str):
        to_delete.remove(item)
        to_delete.add(subflow_indices[item])
        
# Convert the set to a list then delete the indices
sorted_indices = sorted(to_delete, reverse=True)
for index in sorted_indices:
    data.pop(index)

# Writing the modified JSON to the new file
with open(file_path, 'w') as file:
    json.dump(data, file, indent=4)

# Final user prompt for successful operation
print(f"\nMQTT topics have been updated. Modified flows are saved in '{new_file_name}'.")
input("Press Enter to exit.")
