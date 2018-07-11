import psycopg2

# Dictionary where the modified name of the device is the key, and the device object is the value
visited = []

edges = {}
connections = []
data = {}
tol = 0.9


class Connection:
    def __init__(self, name, citation):
        self.name = name
        self.cited = citation
        self.times_cited = ''
        self.shared_authors = []
        self.shared_refs = []


def modify_name(title):
    if type(title) is not str:
        title = title.decode("ascii")
    allowed_char = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    title = ''.join(filter(allowed_char.__contains__, title))
    title = title.lower()
    return title


def initialize_connections(devices):
    for device in devices:
        check_cross_citation(device, devices) # O(n)

    return connections


def check_shared_connections(device, device2, devices, connection):
    shared_authors = check_authors(devices[device2], devices[device])
    shared_references = check_refs(devices[device2], devices[device])

    if shared_authors != [] and shared_references != []:
        connection.shared_refs = shared_references
        connection.shared_authors = shared_authors


def check_authors(device1, device2):
    shared_authors = []
    for author1 in device1.authors:
        author1_split = author1.split(' ')
        for author2 in device2.authors:
            author2_split = author2.split(' ')
            lastname_idx1 = len(author1_split) - 1
            lastname_idx2 = len(author2_split) - 1
            if author1_split[lastname_idx1] == author2_split[lastname_idx2]:
                shared_authors.append(author1)

    return shared_authors


def check_refs(device1, device2):
    shared_refs = []
    for ref1 in device1.backward_ref:
        for ref2 in device2.backward_ref:
            if modify_name(ref1.title) == modify_name(ref2.title):
                shared_refs.append(ref1)

    return shared_refs


def check_cross_citation(device, devices):
    for ref in devices[device].backward_ref:
        is_in_tol, ref_device = within_tol(devices, ref)
        if is_in_tol:
            connection = Connection(devices[device].name, devices[ref_device].name)
            connection.times_cited = ref.timesCited
            check_shared_connections(device, ref_device, devices, connection)
            connections.append(connection)


def within_tol(devices, ref):
    for device in devices:
        tol = calculate_tol(device, modify_name(ref.title))
        if tol > 0.75:
            return True, device
    return False, None


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
    if 0.5 < score < 1:
        print("Comparing %s AND %s. Their tol is %f" % (device, ref, score))
        print("Dif-Count is %d" % dif_count)
    return score


def build_geneology(devices):
    # dict where the device name is the key and the list of other devices is the value
    # initialize the edge-list
    for device in devices:
        device = devices[device]
        if len(device.forward_ref) != 0:
            edges[modify_name(device.name)] = device.forward_ref

# build_JSON(edges)


# def build_JSON(edges):
#     data['root'] = []
#     for edge in edges:
#         if edge not in visited:
#             visited.append(edge)
#             children = create_children(edge)
#
#             new_dict = {
#                 'name': edge,
#                 'children': children
#             }
#             data['root'].append(new_dict)
#
#     with open("Geneology.json", 'w+') as geneology:
#         json.dump(data, geneology)
#
#
# def create_children(name):
#     children = []
#     for child in edges[name]:
#         if child in edges:
#             if child in visited:
#                 new_child = find(child, data['root'])
#                 children.append(new_child)
#
#             else:
#                 visited.append(child)
#                 new_child = {
#                     'name': child,
#                     'children': create_children(child)
#
#                 }
#                 children.append(new_child)
#         else:  # this child has no children of it's own
#             new_child = {
#                 'name': child
#             }
#             children.append(new_child)
#
#     return children
#
#
# #find the dict that has name as one of its keys in a nested dict
#
# def find(name, data):
#     for dict in data:
#         if name != dict['name']:
#             try:
#                 find(name, dict['children'])
#             except:
#                 pass
#
#         else:
#             new_child = dict
#             data.remove(dict)
#             return new_child