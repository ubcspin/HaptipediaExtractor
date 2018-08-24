import psycopg2
import json

from Utilities import modify_name, calculate_tol, is_same_author, check_dates
from CrossReference import create_connection, check_authors, create_crossrefs
from DatabaseFunctionalityModules.DatabaseInfo import connect_to_db, check_table, author_table, pub_table


"""
Device object that simplifies original device object
"""


class DB_Device:
    def __init__(self, device):
        self.id = device[0]
        self.name = device[1]
        self.key = modify_name(device[1])
        self.authors = device[2]
        self.refs = device[3]
        self.backward_refs = device[4]
        self.forward_refs = device[5]
        self.shared_authors = device[6]
        self.shared_refs = device[7]


def check_database():
    conn = connect_to_db()
    if conn is None:
        print("Connection Is None")
        return False
    else:
        try:
            cursor = conn.cursor()
        except Exception as e:
            print(e)
            return False
        finally:
            is_table_ready = check_table(cursor)
            conn.close()
            return is_table_ready


def add_data(new_devices, connections, authors):
    try:
        # use our connection values to establish a connection
        conn = connect_to_db()
        cursor = conn.cursor()

        # #finds new connections between current publications and ones already in the database
        new_connections = find_new_connections(new_devices, cursor)
        connections = {**new_connections, **connections}
        add_devices(new_devices, connections, cursor)
        add_authors(authors, cursor)

        cursor.close()
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def add_authors(authors, cursor):
    authors = get_author_vals(authors)
    authors_in_db = get_authors_in_db(cursor)

    seen_authors = []
    for author in authors:
        for db_author in authors_in_db:
            if is_same_author(author[0], db_author[1]):
                seen_authors.append(author)
                db_author = (db_author[0], db_author[1], db_author[2] + author[1])
                update_author_list(db_author, cursor)

    # seen authors in the end of the first for-loop should have all the authors in our author list thats in our db
    for author in authors:
        if author not in seen_authors:
            add_author(author, cursor)


def add_author(author, cursor):
    add_authors = 'insert into ' + author_table + '(author_name, publications) values (%s, %s)'

    cursor.execute(add_authors, (author[0], author[1]))


def update_author_list(db_author, cursor):
    update_authors = 'update ' + author_table + ' set publications = %s where author_name = %s'

    cursor.execute(update_authors, (db_author[2], db_author[1]))


def get_authors_in_db(cursor):
    get_authors = 'select id, author_name, publications from ' + author_table

    cursor.execute(get_authors)
    authors_in_db = cursor.fetchall()
    return authors_in_db


def get_author_vals(authors):
    authors_val = []
    for author in authors:
        name = author.name
        publication = author.publications
        authors_val.append((name, publication))
    return authors_val


def build_JSON(device, connections):
    shared_authors = []
    shared_refs = []

    for connection in connections:
        connection = connections[connection]
        add_shared_data(connection, device, shared_authors, shared_refs)

    return shared_authors, shared_refs


def add_shared_data(connection, device, shared_authors, shared_refs):
    if device.name == connection.device.name:

        device_shared_authors, device_shared_refs = shared_metadata_to_dict(connection, connection.connected_device.name)
        if len(device_shared_authors) != 0:
            shared_authors.append(device_shared_authors)
        if len(device_shared_refs) != 0:
            shared_refs.append(device_shared_refs)

    if device.name == connection.connected_device.name:

        device_shared_authors, device_shared_refs = shared_metadata_to_dict(connection, connection.device.name)
        if len(device_shared_authors) != 0:
            shared_authors.append(device_shared_authors)
        if len(device_shared_refs) != 0:
            shared_refs.append(device_shared_refs)


def shared_metadata_to_dict(connection, target):
    new_shared_authors = {}
    new_shared_refs = {}
    if len(connection.shared_authors) != 0:
        new_shared_authors["target"] = target
        new_shared_authors["shared_authors"] = connection.shared_authors

    if len(connection.shared_refs) != 0:
        new_shared_refs['target'] = target
        new_shared_refs['shared_refs'] = connection.shared_refs

    return new_shared_authors, new_shared_refs


def get_conn_values(conn):
    paper_1 = conn.device.name
    paper_2 = conn.connected_device.name
    is_cited = conn.is_cited
    times_cited = conn.times_cited
    shared_authors = conn.shared_authors
    shared_refs = conn.shared_refs

    return modify_name(paper_1), paper_1, modify_name(paper_2), paper_2, is_cited, times_cited, shared_authors, shared_refs


def add_devices(new_devices, connections, cursor):
    values = create_values(new_devices, connections)
    command = 'INSERT INTO ' + pub_table + '(title, all_references, authors, abstract, pub_date, publisher,'\
                'sections, figures, backward_refs, forward_refs, shared_authors, shared_refs) '\
                'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '

    for value in values:
        cursor.execute(command, value)


def create_values(devices, connections):
    values = []
    for device in devices:
        name = devices[device].name
        authors = devices[device].authors
        abstract = devices[device].abstract
        date = devices[device].date
        refs = devices[device].refs
        refs = json.dumps(refs)
        publisher = devices[device].publisher
        figures = name + '/Figures/'
        sections = name + '/Sections/Sections.txt'
        back_refs = json.dumps(devices[device].backward_refs)
        forward_refs = json.dumps(devices[device].forward_refs)
        shared_authors, shared_refs = build_JSON(devices[device], connections)
        shared_authors = json.dumps(shared_authors)
        shared_refs = json.dumps(shared_refs)

        data = (name, refs, authors, abstract, date, publisher, sections, figures, back_refs, forward_refs,
                shared_authors, shared_refs)
        values.append(data)

    return values


def find_new_connections(new_devices, cursor):
    db_devices = get_devices_from_db(cursor)
    authors = get_authors_in_db(cursor)
    updated_db_devices = []
    new_connections = {}

    for new_device in new_devices:
        new_device = new_devices[new_device]
        for device in db_devices:
            db_device = DB_Device(device)
            if new_device.name != db_device.name:
                connection = find_connection(new_device, db_device, authors)
                if connection is not None:
                    new_connections[connection.key] = connection

    create_crossrefs(new_connections)
    updated_devices = update_shared_data(new_connections, db_devices)
    update_db_devices(updated_devices, cursor)
    return new_connections


def update_shared_data(new_connections, devices):
    updated_devices = []
    for device in devices:
        device = DB_Device(device)
        shared_authors, shared_refs = build_JSON(device, new_connections)
        device.shared_authors = device.shared_authors + shared_authors
        device.shared_refs = device.shared_refs + shared_refs
        updated_devices.append(device)

    return updated_devices


def update_db_devices(devices, cursor):
    update_db = 'update ' + pub_table + ' set backward_refs = %s, forward_refs = %s, shared_authors = %s,'\
                'shared_refs = %s where id = %s'

    for device in devices:
        updated_shared_authors = json.dumps(device.shared_authors)
        updated_shared_refs = json.dumps(device.shared_refs)
        updated_back_refs = json.dumps(device.backward_refs)
        updated_forward_refs = json.dumps(device.forward_refs)
        cursor.execute(update_db, (updated_back_refs, updated_forward_refs, updated_shared_authors, updated_shared_refs, device.id))


def get_devices_from_db(cursor):
    command = 'select id, title, authors, all_references, backward_refs, forward_refs, shared_authors, shared_refs from ' + pub_table

    cursor.execute(command)
    devices = cursor.fetchall()
    return devices


def find_connection(new_device, device, authors):

    is_cited, times_cited, is_backref = compare_crossrefs(new_device, device)
    shared_authors, shared_refs = find_shared_metadata(new_device, device, authors)

    if is_cited or shared_refs != [] or shared_authors != []:
        if is_backref:
            connection = create_connection(new_device, device, is_cited, times_cited, shared_authors, shared_refs)
        else:
            connection = create_connection(device, new_device, is_cited, times_cited, shared_authors, shared_refs)

        return connection


def find_shared_metadata(new_device, device, authors):
    shared_authors = check_authors(new_device, device, authors)
    shared_references = check_refs(new_device, device)

    return shared_authors, shared_references


def check_authors(new_device, db_device, authors):
    shared_authors = []
    for author in new_device.authors:
        for author_id in db_device.authors:
            db_author_name = get_author_name(author_id, authors)
            if is_same_author(author, db_author_name):
                shared_authors.append(db_author_name)
    return shared_authors


def get_author_name(author_id, authors):
    for author in authors:
        if author_id == str(author[0]):
            return author[1]

    return ''


def check_refs(new_device, device):
    shared_refs = []
    for ref_0 in new_device.refs:
        for ref_1 in device.refs:
            tol = calculate_tol(modify_name(ref_0['title']), modify_name(ref_1['title']))
            if tol > 0.75 and check_dates(ref_0, ref_1):
                shared_refs.append(ref_1)

    return shared_refs


# checks if new_device cites device
def compare_crossrefs(new_device, device):
    for ref in new_device.refs:
        score = calculate_tol(modify_name(ref['title']), device.key)
        if score > 0.75:
            return True, ref['times_cited'], True

    for ref in device.refs:
        score = calculate_tol(modify_name(ref['title']), new_device.key)
        if score > 0.75:
            return True, ref['times_cited'], False

    return False, 0, False



