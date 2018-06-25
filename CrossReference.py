import json
# Dictionary where the modified name of the device is the key, and the device object is the value
visited = []
edges = {}
data = {}


def modify_name(title):
    if type(title) is not str:
        title = title.decode("ascii")
    allowed_char = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    title = ''.join(filter(allowed_char.__contains__, title))
    title = title.lower()
    return title


def build_geneology(devices):
    # dict where the device name is the key and the list of other devices is the value
    # initialize the edge-list
    for device in devices:
        device = devices[device]
        if len(device.forward_ref) != 0:
            edges[modify_name(device.name)] = device.forward_ref

    build_JSON(edges)


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
            try:
                find(name, dict['children'])
            except:
                pass

        else:
            new_child = dict
            data.remove(dict)
            return new_child