import json
import os

# Filename of the original Node-RED flows file
original_file_name = 'flows.json'

# Base filename for the new file where the modified JSON will be saved
base_new_file_name = 'new_flows'

# Check if the new file name already exists and modify it if necessary
counter = 1 
new_file_name = f"{base_new_file_name}.json" 

# Loop to find a unique file name by appending a counter
while os.path.exists(new_file_name):
    new_file_name = f"{base_new_file_name}_{counter}.json"
    counter += 1

# Load the JSON data from the original file
with open(original_file_name, 'r') as file:
    data = json.load(file)

# Output to user what information is needed
instructions = """ You will need:
- Number of stations
- Station names as they appear in MQTT topics
- The bucket state MQTT topic for the first station
"""
print(instructions)

# Ask the user how many stations there are, and get station names
num_stations = int(input("Enter the number of stations that will be displayed on the dashboard: "))
station_names = []
display_names = []
for i in range(num_stations):
    station_name = input(f"\nEnter the name for station {i+1} as it appears in an **MQTT topic**: ")
    display_name = input(f"Enter the name for station {i+1} that you would like to appear on the dashboard: ")
    station_names.append(station_name)
    display_names.append(display_name)
    
# Ask the user for the new MQTT topics
print("\nThe following MQTT topic is for the first station of the line.")
bucket_state_topic = input("Enter the bucket state topic: ")
system_events_topic = bucket_state_topic.replace('production/bucketstate', 'systemevents')
tracking_topic = bucket_state_topic.replace('production/bucketstate', 'tracking')
likely_topic = bucket_state_topic.replace('bucketstate', 'likely')
production_topic = bucket_state_topic.replace('/bucketstate', '')
andons_topic = bucket_state_topic.replace('production/bucketstate', 'andonevents')

# Iterate through each element in the JSON data
for node in data:
    node_type = node.get('type')
    node_name = node.get('name')
    
    if node.get('type') == 'mqtt in':    
        if 'Bucket State' in node_name:
            topic = bucket_state_topic
        elif 'System Events' in node_name:
            topic = system_events_topic
        elif 'Tracking' in node_name:
            topic = tracking_topic
        elif 'Likely' in node_name:
            topic = likely_topic
        elif 'Production' in node_name:
            topic = production_topic
        elif 'Andon Events' in node_name:
            topic = andons_topic
            
        if node_name[-1].isdigit():
            station_number = int(node_name[-1]) - 1
            node['topic'] = topic.replace(station_names[0], station_names[station_number])
        else:
            node['topic'] = topic
       
    elif node.get('type') == 'ui_tab':
        if node_name[-1].isdigit():
            station_number = int(node_name[-1]) - 1
            node['name'] = display_names[station_number]

# Write the modified JSON data to the new file
with open(new_file_name, 'w') as file:
    json.dump(data, file, indent=4)

print(f"\nMQTT topics have been updated. Modified flows are saved in '{new_file_name}'.")
input("Press Enter to exit.")
