import json
# Dictionary where the modified name of the device is the key, and the device object is the value
devices = {}
visited = []
edges = {}
data = {}

# Device class to represent a single data extracted from a PDF


class Device:

    def __init__(self, name):
        self.name = name
        self.backward_ref = []
        self.forward_ref = []
        self.authors = []  # filled when we create the author parser


def init_device(name):
    # this assumes that a session has already been created
    new_device = Device(name)
    modified_name = modify_name(name)
    # add_forward_ref(new_device, modified_name, False, None)
    devices[modified_name] = new_device

    return new_device, modified_name

# Parameters:
# this_device: device
# name
# isInitialized: if true, check if the ref of this_device is in devices, update the forwardRef
#                if false, check if this_device has been referenced before (ref will be None)
# ref: reference to check is it exists


def add_forward_ref(this_device, name, isInitialized, ref):
    if isInitialized:
        ref = modify_name(ref)
        if ref in devices:
            device = devices[ref]
            device.forward_ref.append(modify_name(name))

    else:
        # n^2, see if a different implementation can change this
        for device in devices:
            for back_ref in devices[device].backward_ref:
                if back_ref == name:
                    cited_by = modify_name(devices[device].name)
                    this_device.forward_ref.append(cited_by)
                    print("Added Forward Ref: " + str(this_device.name) + "was referred by " + cited_by)


# Parameters:
# device: device where backwardRef should be added
# ref_name: name of the reference (not modified)
def add_backward_ref(device, ref_name):

    ref_name = modify_name(ref_name)
    device.backward_ref.append(ref_name)


def modify_name(title):
    if type(title) is not str:
        title = title.decode("ascii")
    allowed_char = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    title = ''.join(filter(allowed_char.__contains__, title))
    title = title.lower()
    return title


def build_geneology():
    # dict where the device name is the key and the list of other devices is the value
    initialize_forward_ref()
    # initialize the edge-list
    for device in devices:
        device = devices[device]
        if len(device.forward_ref) != 0:
             edges[modify_name(device.name)] = device.forward_ref

    build_data(edges)


def initialize_forward_ref():
    for device in devices:
        for ref in devices[device].backward_ref:
            if ref in devices:
                devices[ref].forward_ref.append(device)

def build_data(edges):
    data['root'] = []
    for edge in edges:
        visited.append(edge)
        children = []
        children = create_children(edge)

        new_dict = {
            'name': edge,
            'children': children
        }
        data['root'].append(new_dict)

    with open("Geneology.json", 'w+') as geneology:
        json.dump(data, geneology)


def create_children(name):
    children = []
    for child in edges[name]:
        if child in edges:
            if child in visited:
                new_child = find(child, data['root'])
                children.append(new_child)

            else:
                visited.append(visited)
                new_child = {
                    'name' : child,
                    'children' : create_children(name)

                }
                children.append(new_child)
        else:  # this child has no children of it's own
            new_child = {
                'name': child
            }
            children.append(new_child)

    return children


#find the dict that has name as one of its keys in a nested dict

def find(name, data):
    for dict in data:
        if name != dict['name']:
            find(name, dict['children'])

        else:
            new_child = dict
            data.remove(dict)
            return new_child

























