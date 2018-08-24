import re
import time
from Utilities import calculate_tol, modify_name, is_same_author, check_dates
"""
Use a dictionary for visited connections to reduce runtime in lookup
Since __contains__ function in dict are implemented with a hashtable
Key is a string with the names of connected device, Value is the connection itself
"""
visited_connections = {}

edges = {}
connections = {}

"""
Connection class to capture connections between two papers
- whether one paper cited the other paper
- do both papers share some references
- do both papers share some authors
"""


class Connection:
    def __init__(self, device, connected_device):
        self.device = device
        self.connected_device = connected_device
        self.key = device.name + connected_device.name
        self.is_cited = False
        self.times_cited = ''
        self.shared_authors = []
        self.shared_refs = []

    def __eq__(self, other):
        return self.device.name == other.device.name and self.connected_device.name == other.connected_device.name



"""
initialize_connections(devices)

Purpose: Compares all possible pairs of devices to see if there exists a connection between them
Parameters: devices - List of devices
Returns: all connections found
"""


def initialize_connections(devices):
    count = 1
    start = time.time()
    for device in devices:
        for comparison_device in devices:
            if device != comparison_device:
                comp_device = devices[comparison_device]
                main_device = devices[device]
                check_connection(main_device, comp_device)
        finish = time.time()
        print("Average time taken for %s is %s" % (str(count), str((finish - start)/count)))
        count += 1

    create_crossrefs(connections)

    return connections


def create_crossrefs(connections):
    for conn in connections:
        conn = connections[conn]
        if conn.is_cited:
            conn.device.backward_refs.append({'target': conn.connected_device.name, 'times_cited': conn.times_cited})
            conn.connected_device.forward_refs.append({'target': conn.device.name, 'times_cited': conn.times_cited})


"""
in_visited(device, comp_device)

Purpose: to check if we've seen these pair of devices before, checks if the names have appeared as a key in
         visited_connections dictionary
Parameters: device - first device in the pair to compare
            comp_device  - second device in the pair to compare
Returns: Boolean on whether the pair was seen or not
"""


def in_visited(device, comp_device):

    test_key1 = device.name + comp_device.name
    test_key2 = comp_device.name + device.name

    if test_key1 in visited_connections or test_key2 in visited_connections:
        return True
    else:
        return False


"""
find_shared_metadata(device, comp_device)

Purpose: calls check_authors and check_refs to find shared authors and shared references
Returns: Tuple where the first index is the shared authors and the second index is the shared references
"""


def find_shared_metadata(device, comp_device):
    shared_authors = check_authors(device, comp_device)
    shared_references = check_refs(device, comp_device)

    return shared_authors, shared_references


"""
check_authors(device1, device2)

Purpose: finds the shared authors between two devices by comparing both lastname and firstname 
Parameters: device1 - first device in comparison 
            device2 - second device in comparison
Returns: List of shared authors
"""


def check_authors(device1, device2):
    shared_authors = []
    for author1 in device1.authors:
        for author2 in device2.authors:
            if is_same_author(author1, author2):
                shared_authors.append(author1)

    return shared_authors


"""
check_refs(device1, device2)

Purpose: checks for shared references between device1 and device2 by comparing reference titles and the years they were 
         published 
Parameters: device1 - first device in the comparison
            device2 - second device in the comparison
Returns: List of shared reference objects
"""


def check_refs(device1, device2):
    shared_refs = []
    for ref1 in device1.refs:
        for ref2 in device2.refs:
            tol = calculate_tol(ref1['title'], ref2['title'])
            if tol > 0.75 and check_dates(ref1, ref2):
                shared_refs.append(ref1)

    return shared_refs


"""
Checks if there is a connection between these two devices
"""


def check_connection(device, comp_device):

    if not in_visited(device, comp_device):

        # check if devices cite each other and share any refs and authors
        is_cited, times_cited, device_cited_comp_device = check_crossref(device, comp_device)
        shared_authors, shared_refs = find_shared_metadata(device, comp_device)
        visited_connections[device.name + comp_device.name] = (device, comp_device)

        if is_cited:
            if device_cited_comp_device:
                connection = create_connection(device, comp_device, is_cited, times_cited, shared_authors, shared_refs)

            else:
                connection = create_connection(comp_device, device, is_cited, times_cited, shared_authors, shared_refs)
            connections[connection.key] = connection

        else:
            if shared_authors != [] or shared_refs != []:
                connection = create_connection(device, comp_device, is_cited, times_cited, shared_authors, shared_refs)
                connections[connection.key] = connection


# def update_connection(device, comp_device, is_cited, times_cited):
#     key_to_update = device.name + comp_device.name
#     key_to_delete = comp_device.name + device.name
#
#     shared_authors = []
#     shared_refs = []
#
#     if key_to_delete in connections:
#         shared_authors = connections[key_to_delete].shared_authors
#         shared_refs = connections[key_to_delete].shared_refs
#         del connections[key_to_delete]
#
#     if key_to_update in connections:
#         old_connection = connections[key_to_update]
#         old_connection.is_cited = is_cited
#         old_connection.times_cited = times_cited
#     else:
#         connection = create_connection(device, comp_device, is_cited, times_cited, shared_authors, shared_refs)
#         connections[connection.key] = connection


def create_connection(device, comp_device, is_cited, times_cited, shared_authors, shared_refs):
    connection = Connection(device, comp_device)
    connection.is_cited = is_cited
    connection.times_cited = times_cited
    connection.shared_authors = shared_authors
    connection.shared_refs = shared_refs

    # print('Connection created between %s and %s' %(device.name, comp_device.name))
    return connection


"""
Checks whether both devices cited each other
Returns: 
is_cited: whether they cited each other or not
times_cited: the number of times one device cited the other, if they didn't cite, set to 0
device_cited_comp_device: if true, device cited comp_device. if false, comp_device cited device
"""


def check_crossref(device, comp_device):
    for ref in device.refs:
        score = calculate_tol(comp_device.key, modify_name(ref['title']))
        if score > 0.75:
            return True, ref['times_cited'], True

    for ref in comp_device.refs:
        score = calculate_tol(device.key, modify_name(ref['title']))
        if score > 0.75:
            return True, ref['times_cited'], False

    return False, 0, False








