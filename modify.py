import json
import os
from helper import *

# File setup for loading and saving JSON
original_file_name = 'flows.json'
base_new_file_name = 'new_flows'
counter = 1
new_file_name = f"{base_new_file_name}.json"

# Ensuring the output file name is unique by incrementing a counter if the file already exists
while os.path.exists(new_file_name):
    new_file_name = f"{base_new_file_name}_{counter}.json"
    counter += 1

# Loading the original JSON data from file
with open(original_file_name, 'r') as file:
    data = json.load(file)

# Prompting user for initial setup information
print(""" You will need:
- Number of stations
- Station names as they appear in MQTT topics
- The bucket state MQTT topic for the first station
""")

# Input validation for the number of stations
while True:
    try:
        num_stations = int(input("Enter the number of stations that will be displayed on the dashboard: "))
        if 2 <= num_stations <= 12:
            break
        else:
            print("Please enter an integer between 4 and 12.")
    except ValueError:
        print("Invalid input. Please enter an integer.")

station_names = []
display_names = []

# Collecting station names and display names with validation
for i in range(num_stations):
    while True:
        station_name = input(f"\nEnter the name for station {i+1} as it appears in an MQTT TOPIC: ")
        if ' ' not in station_name:
            station_names.append(station_name)
            break
        else:
            print("The station name cannot contain spaces.")

    while True:
        display_name = input(f"Enter the name for station {i+1} that you would like to appear on the dashboard: ")
        if len(display_name) <= 16:
            display_names.append(display_name)
            break
        else:
            print("The display name must be 16 characters or less.")

# Input validation for MQTT topic for the first station
while True:
    bucket_state_topic = input("\nEnter the bucket state topic for the first station: ")
    if '/' in bucket_state_topic and ' ' not in bucket_state_topic:
        break
    else:
        print("Enter a valid MQTT topic.")

# Define a dictionary to map 'type' strings to topics dynamically
topics = {
    'Bucket State': bucket_state_topic,
    'System Events': bucket_state_topic.replace('production/bucketstate', 'systemevents'),
    'Tracking': bucket_state_topic.replace('production/bucketstate', 'tracking'),
    'Likely': bucket_state_topic.replace('bucketstate', 'likely'),
    'Production': bucket_state_topic.replace('/bucketstate', ''),
    'Andon Events': bucket_state_topic.replace('production/bucketstate', 'andonevents')
}

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
        for key in topics:
            if key in node_name:
                topic = topics[key]
                station_number = extract_station_number(node_name)
                if station_number is not None:
                    if station_number < num_stations:
                        node['topic'] = topic.replace(station_names[0], station_names[station_number])
                    else:
                        attached_subflow = node['wires'][0][0]
                        subflows_to_delete.add(attached_subflow)
                        indices_to_delete.add(index)
                else:
                    if 'Likely' in node['name']:
                        node['topic'] = topics['Likely']
                    elif 'Production' in node['name']:
                        node['topic'] = topics['Production']
       
    elif node_type == 'ui_tab':
        station_number = extract_station_number(node_name)
        if station_number is not None:
            if station_number < num_stations:
                node['name'] = display_names[station_number]
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
with open(new_file_name, 'w') as file:
    json.dump(data, file, indent=4)

# Final user prompt for successful operation
print(f"\nMQTT topics have been updated. Modified flows are saved in '{new_file_name}'.")
input("Press Enter to exit.")
