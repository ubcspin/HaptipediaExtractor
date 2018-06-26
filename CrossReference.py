import json
import re
# Dictionary where the modified name of the device is the key, and the device object is the value
visited = []
edges = {}
data = {}
tol = 0.9


def modify_name(title):
    if type(title) is not str:
        title = title.decode("ascii")
    allowed_char = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    title = ''.join(filter(allowed_char.__contains__, title))
    title = title.lower()
    return title


def initialize_forward_ref(devices):
    for device in devices:
        for ref in devices[device].backward_ref:
            if ref in devices:
                devices[ref].forward_ref.append(device)

def initialize_cross_ref(devices):
    for device in devices:
        for ref in devices[device].backward_ref:
            if within_tol(devices, ref):
                devices[ref].forward_ref.append(device)


def within_tol(devices, ref):
    for device in devices:
        tol = calculate_tol(device, ref)
        if tol > 0.75:
            return True
    return False


def calculate_tol(device, ref):
    reflist = ref.split(' ')
    device_str_list = device.split(' ')

    score = 0

    if len(reflist) < len(device_str_list):
        lower_bound = len(reflist)
        upper_bound = len(device_str_list)
    else:
        lower_bound = len(device_str_list)
        upper_bound = len(reflist)

    i = 0
    while i < lower_bound:
        if i == 0:
            if reflist[i] == device_str_list[i] or reflist[i] == device_str_list[i+1] or reflist[i+1] == device_str_list[i]:
                score += 1
        else:
            if reflist[i] == device_str_list[i]:
                score += 1
            elif i+1 < upper_bound and i+1 < lower_bound:
                if reflist[i] == device_str_list[i + 1] or reflist[i + 1] == device_str_list[i]:
                    score += 1

        i += 1

    score = score/upper_bound
    if score > 0.75:
        print("Comparing %s and %s. Their tol is %f" % (device, ref, score))
    return score


        # if i < len(device_str_list):
        #     if i == 0:
        #         if reflist[i] == device_str_list[i]:
        #             score +=1
        #         elif i + 1 < len(device_str_list):
        #             if reflist[i] == device_str_list[i+1]:
        #                 score += 1
        #     elif i == len(reflist) - 1:
        #         if reflist[i] == device_str_list[i] or reflist[i] == device_str_list[i-1]:
        #             score += 1
        #         elif i + 1 < len(device_str_list):
        #             if reflist[i] == device_str_list[i+1]:
        #                 score += 1
        #     else:
        #         if reflist[i] == device_str_list[i] or reflist[i] == device_str_list[i-1]:
        #             score += 1
        #         elif i + 1 < len(device_str_list):
        #             if reflist[i] == device_str_list[i+1]:
        #                 score += 1


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