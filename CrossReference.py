
"""
Use a dictionary for visited connections to reduce runtime in lookup
Since __contains__ function in dict are implemented with a hashtable, runtime is reduced
Key is a string with the names of connected device, Value is the connection itself
"""
visited_connections = {}

edges = {}
connections = {}


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
    allowed_char = set('abcdefghijklmnopqrstuvwxyz\/- ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789   ')
    title = ''.join(filter(allowed_char.__contains__, title))
    title = title.lower()
    return title


def initialize_connections(devices):
    for device in devices:
        for comparison_device in devices:
            if device != comparison_device:
                # use the values instead of keys
                comp_device = devices[comparison_device]
                main_device = devices[device]
                check_connection(main_device, comp_device)

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
    for ref1 in device1.backward_ref:
        for ref2 in device2.backward_ref:
            tol = calculate_tol(ref1.key, ref2.key)
            if tol > 0.75:
                shared_refs.append(ref1)

    return shared_refs


def check_connection(device, comp_device):

    is_cited, times_cited = check_crossref(device, comp_device)
    connection_seen = in_visited(device, comp_device)

    if connection_seen and is_cited:
        update_connection(device, comp_device, is_cited, times_cited)

    else:
        if not connection_seen:
            key = device.name + comp_device.name
            visited_connections[key] = (device, comp_device)
            shared_authors, shared_refs = find_shared_metadata(device, comp_device)
            if shared_authors != [] or shared_refs != [] or is_cited:
                connection = create_connection(device, comp_device, is_cited, times_cited, shared_authors, shared_refs)
                connections[connection.key] = connection


def update_connection(device, comp_device, is_cited, times_cited):
    key_to_update = device.name + comp_device.name
    key_to_delete = comp_device.name + device.name

    shared_authors = []
    shared_refs = []

    if key_to_delete in connections:
        shared_authors = connections[key_to_delete].shared_authors
        shared_refs = connections[key_to_delete].shared_refs
        del connections[key_to_delete]

    if key_to_update in connections:
        old_connection = connections[key_to_update]
        old_connection.is_cited = is_cited
        old_connection.times_cited = times_cited
    else:
        connection = create_connection(device, comp_device, is_cited, times_cited, shared_authors, shared_refs)
        connections[connection.key] = connection


def create_connection(device, comp_device, is_cited, times_cited, shared_authors, shared_refs):
    connection = Connection(device, comp_device)
    connection.is_cited = is_cited
    connection.times_cited = times_cited
    connection.shared_authors = shared_authors
    connection.shared_refs = shared_refs

    # print('Connection created between %s and %s' %(device.name, comp_device.name))
    return connection


def check_crossref(device, comp_device):
    for ref in device.backward_ref:
        score = calculate_tol(comp_device.key, modify_name(ref.title))
        if score > 0.75:
            return True, ref.timesCited

    return False, 0


def calculate_tol(device, ref):
    reflist = ref.split(' ')
    device_str_list = device.split(' ')

    score = 0
    dif_count = 0

    if len(reflist) < len(device_str_list):
        lower_bound = len(reflist)
        upper_bound = len(device_str_list)
    else:
        lower_bound = len(device_str_list)
        upper_bound = len(reflist)

    i = 0
    while i < lower_bound:
        if i == 0:
            if reflist[i] == device_str_list[i]:
                score += 1
            elif i+1 < upper_bound and i+1 < lower_bound:
                if reflist[i] == device_str_list[i+1] or reflist[i+1] == device_str_list[i]:
                    score += 1
                    dif_count += 1

        else:
            if reflist[i] == device_str_list[i]:
                score += 1
            elif i+1 < upper_bound and i+1 < lower_bound:
                if reflist[i] == device_str_list[i + 1] or reflist[i + 1] == device_str_list[i]:
                    score += 1
                    dif_count += 1

        i += 1

    score = score/upper_bound
    # if 0.75 < score:
    #     print("Comparing %s AND %s. Their tol is %f" % (device, ref, score))
    #     print("Dif-Count is %d" % dif_count)
    return score





