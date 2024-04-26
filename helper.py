# Find the station number from the MQTT in node name. Station 1 starts at 0
def extract_station_number(node_name):
    import re
    match = re.search(r'\d+$', node_name)
    if match:
        return int(match.group()) - 1
    else:
        return None 
        
        
# Get the group id of a certain multi or single station views
def get_group_id(view_type, station_number):
    single_station_groups = {
        1: '8bd8cbf3c40f1f99',
        2: 'b114a68376e01b10',
        3: '12ebaf6110cabd38',
        4: '26c9438cdf6ae260',
        5: '2e1da0c7f19845cd',
        6: '8bfc58d1d11203a5',
        7: 'eec6fc29325eb423',
        8: 'c959665501acccad',
        9: '578a0a48150a5041',
        10: 'fe27d477317c1d1d',
        11: 'd8e55885f2fba42a',
        12: '744638d47e910719'
    }

    multi_station_groups = {
        1: '0373f32ace576561',
        2: '951d70129c877b2e',
        3: 'fd17cfd0eda5af83',
        4: 'cd5ad1d0bf7f8611',
        5: 'c263be4ca6df137a',
        6: '519feba73659cca7',
        7: '77eddc1de9c1ddaf',
        8: 'dbbee0761b1258b4',
        9: 'e4fbc8a4df7e3429',
        10: 'fe00eb86e5ca025b',
        11: '91c33a1c95225876',
        12: '485f70f4c6baeff8'
    }
    
    if view_type == 'multi':
        return multi_station_groups[station_number]
    elif view_type == 'single':
        return single_station_groups[station_number]
    

# Get single station view from group id
def get_station_from_group(group_id):
    single_station_groups = {
        '8bd8cbf3c40f1f99': 1,
        'b114a68376e01b10': 2,
        '12ebaf6110cabd38': 3,
        '26c9438cdf6ae260': 4,
        '2e1da0c7f19845cd': 5,
        '8bfc58d1d11203a5': 6,
        'eec6fc29325eb423': 7,
        'c959665501acccad': 8,
        '578a0a48150a5041': 9,
        'fe27d477317c1d1d': 10,
        'd8e55885f2fba42a': 11,
        '744638d47e910719': 12
    }
    
    if group_id in single_station_groups:
        return single_station_groups[group_id]


# Remove node if greater than the station number
def check_to_remove_node(data, node, num_stations):
    station_number = extract_station_number(node['name'])
    if station_number is not None and station_number >= num_stations:
        data.remove(node)