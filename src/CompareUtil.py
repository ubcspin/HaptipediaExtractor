import re

"""
Module to compare authors, titles and references
"""


"""
modify_name(title)

Purpose: - changes titles by removing special characters and making all chars lowercase,
         - used for when comparing two strings so titles are uniform
Parameters: title - title to be modified
Returns: modified title
"""


def modify_name(title):
    if type(title) is not str:
        title = title.decode("ascii")
    allowed_char = set('abcdefghijklmnopqrstuvwxyz\/- ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    title = ''.join(filter(allowed_char.__contains__, title))
    title = title.lower()
    return title


"""
Author Comparison function
"""


def is_same_author(author1, author2):
    author1_split = author1.split(' ')
    author2_split = author2.split(' ')
    lastname_idx1 = len(author1_split) - 1
    lastname_idx2 = len(author2_split) - 1
    if author1_split[lastname_idx1] == author2_split[lastname_idx2]:
        if len(author1_split) > 1 and len(author2_split) > 1:
            firstname1 = author1_split[0]
            firstname2 = author2_split[0]
            if firstname1 == firstname2:
                return True
            # if their first full names aren't exactly right, should we still check just the first letter?
            elif firstname1[0] == firstname2[0]:
                return True
            else:
                return False
    else:
        return False


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