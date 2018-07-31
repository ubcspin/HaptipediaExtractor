import re
import time
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


def modify_name(title):
    if type(title) is not str:
        title = title.decode("ascii")
    allowed_char = set('abcdefghijklmnopqrstuvwxyz\/- ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    title = ''.join(filter(allowed_char.__contains__, title))
    title = title.lower()
    return title


"""
Compares each device with each other and check if there exists a connection between them.
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

    return connections


def in_visited(device, comp_device):

    test_key1 = device.name + comp_device.name
    test_key2 = comp_device.name + device.name

    if test_key1 in visited_connections or test_key2 in visited_connections:
        return True
    else:
        return False


def find_shared_metadata(device, comp_device):
    shared_authors = check_authors(device, comp_device)
    shared_references = check_refs(device, comp_device)

    return shared_authors, shared_references


def check_authors(device1, device2):
    shared_authors = []
    for author1 in device1.authors:
        author1_split = author1.split(' ')
        for author2 in device2.authors:
            author2_split = author2.split(' ')
            lastname_idx1 = len(author1_split) - 1
            lastname_idx2 = len(author2_split) - 1
            same_firstname = True
            if len(author1_split) > 1 and len(author2_split) > 1:
                firstname1 = author1_split[0]
                firstname2 = author2_split[0]
                if firstname1 == firstname2:
                    same_firstname = True
                elif firstname1[0] == firstname2[0]:
                    same_firstname = True
                else:
                    same_firstname = False
            same_lastname = author1_split[lastname_idx1] == author2_split[lastname_idx2]
            if same_firstname and same_lastname:
                shared_authors.append(author1)

    return shared_authors


def check_refs(device1, device2):
    shared_refs = []
    for ref1 in device1.refs:
        for ref2 in device2.refs:
            tol = calculate_tol(ref1, ref2)
            if tol > 0.75:
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
    for ref in device.backward_ref:
        score = calculate_tol(comp_device.key, modify_name(ref.title))
        if score > 0.70:
            return True, ref.timesCited, True

    for ref in comp_device.backward_ref:
        score = calculate_tol(device.key, modify_name(ref.title))
        if score > 0.70:
            return True, ref.timesCited, False

    return False, 0, False


"""
Calculates how similar one name is compared to another
"""
def calculate_tol(device, ref):
    device = modify_name(device)
    ref = modify_name(ref)
    reflist = re.split(r' |-', ref)
    device_str_list = re.split(r' |-', device)

    score = 0
    dif_count = 0

    if len(reflist) < len(device_str_list):
        lower_bound = reflist
        upper_bound = device_str_list
    else:
        lower_bound = device_str_list
        upper_bound = reflist

    i = 0
    while i < len(lower_bound):
        if lower_bound[i] == upper_bound[i]:
            score += 1
        elif i+1 < len(upper_bound):
            if i+1 < len(lower_bound):
                if lower_bound[i] == upper_bound[i+1] or upper_bound[i+1] == lower_bound[i]:
                    score += 1
                else:
                    dif_count += 1
            else:
                if lower_bound[i] == upper_bound[i+1]:
                    score += 1
                else:
                    dif_count += 1

        i += 1

    score = (score - dif_count)/len(lower_bound)
    # if 0.85 > score and score > 0.5:
        # str = "Comparing %s AND %s. Their tol is %f" % (device, ref, score)
        # connections_to_check.append(str)
    return score





