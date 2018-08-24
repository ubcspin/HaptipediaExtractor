from Utilities import is_same_author

authors = []


class Author:
    def __init__(self, name):
        self.name = name
        self.publications = []

    def __eq__(self, other):
        return is_same_author(self.name, other.name)


def build_author_list(devices):
    for device in devices:
        for author in devices[device].authors:
            has_seen, author_obj = has_seen_author(author)
            if has_seen:
                author_obj.publications.append(devices[device].name)
            else:
                new_author = Author(author)
                new_author.publications.append(devices[device].name)
                authors.append(new_author)

    return authors


def has_seen_author(author):
    for auth in authors:
        if is_same_author(author, auth.name):
            return True, auth
    return False, None
