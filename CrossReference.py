import json
# Dictionary where the modified name of the device is the key, and the device object is the value
devices = {}
visited = []
edges = {}
data = {}

# Device class to represent a single data extracted from a PDF


class Device:

    def __init__(self, name):
        self.name = name #also the name of the folder it's in
        self.backward_ref = []
        self.forward_ref = []
        self.authors = []
        self.publisher = ''
        self.sections = {}
        self.figures = {}
        self.citations = []


def init_device(name):
    # this assumes that a session has already been created
    new_device = Device(name)
    modified_name = modify_name(name)
    # add_forward_ref(new_device, modified_name, False, None)
    devices[modified_name] = new_device

    return new_device

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

    build_JSON(edges)


def initialize_forward_ref():
    for device in devices:
        for ref in devices[device].backward_ref:
            if ref in devices:
                devices[ref].forward_ref.append(device)


def build_JSON(edges):
    data['root'] = []
    for edge in edges:
        if edge not in visited:
            visited.append(edge)
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
                visited.append(child)
                new_child = {
                    'name': child,
                    'children': create_children(child)

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