import psycopg2

from CompareUtil import modify_name, calculate_tol, is_same_author
from CrossReference import create_connection, check_authors, create_crossrefs

"""
Database Schema not finalized yet
"""

"""
Device object that simplifies original device object
"""

class DB_Device:
    def __init__(self, id, name, authors, refs, backward_refs, citations):
        self.id = id
        self.name = name
        self.key = modify_name(name)
        self.authors = authors
        self.refs = refs
        self.back_references = backward_refs
        self.citations = citations


def add_data(new_devices, connections, authors):
    try:
        # use our connection values to establish a connection
        conn = psycopg2.connect(host='localhost', dbname='testpaperdb', user='postgres', password='postgres',
                                port='5433')
        # create a psycopg2 cursor that can execute queries
        cursor = conn.cursor()

        #finds new connections between current publications and ones already in the database
        new_connections = find_new_connections(new_devices, cursor)
        # to_add_connections = {**connections, **new_connections}
        add_devices(new_devices, cursor)
        add_authors(authors, cursor)
        # add_connections(to_add_connections)

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
            if is_same_author(author[0], db_author[0]):
                seen_authors.append(author)
                db_author = (db_author[0], db_author[1] + author[1])
                update_author_list(db_author, cursor)

    # seen authors in the end of the first for-loop should have all the authors in our author list thats in our db
    for author in authors:
        if author not in seen_authors:
            add_author(author, cursor)


def add_author(author, cursor):
    command = """
                insert into prototype_data.authors(author_name, publications)
                values (%s, %s)
              """

    cursor.execute(command, (author[0], author[1]))


def update_author_list(db_author, cursor):
    update = """
                update prototype_data.authors set publications = %s where author_name = %s
             """
    cursor.execute(update, (db_author[1], db_author[0]))


def get_authors_in_db(cursor):
    get_authors = """
                    select author_name, publications from prototype_data.authors
                  """

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


def add_connections(connections):
    command = """ insert into connections (paper_1id, paper_1, paper_2id, paper_2, is_cited, times_cited, shared_authors, shared_refs)
                                values (%s, %s, %s, %s, %s, %s, %s, %s) """

    try:
        # use our connection values to establish a connection
        conn = psycopg2.connect(host='localhost', dbname='testpaperdb', user='postgres', password='postgres',
                                port='5433')
        # create a psycopg2 cursor that can execute queries
        cursor = conn.cursor()
        for connection in connections:
            try:
                values = get_conn_values(connections[connection])
                cursor.execute(command, values)
            except Exception as e:
                print(e)
                pass
        cursor.close()
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def get_conn_values(conn):
    paper_1 = conn.device.name
    paper_2 = conn.connected_device.name
    is_cited = conn.is_cited
    times_cited = conn.times_cited
    shared_authors = conn.shared_authors
    shared_refs = conn.shared_refs

    return modify_name(paper_1), paper_1, modify_name(paper_2), paper_2, is_cited, times_cited, shared_authors, shared_refs


def add_devices(new_devices, cursor):
    values = create_values(new_devices)
    command = """
                INSERT INTO prototype_data.publications(title, all_references, authors, abstract, pub_date, publisher, 
                sections, figures, refs, citations) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
              """
    for value in values:
        cursor.execute(command, value)


def create_values(devices):
    values = []
    for device in devices:
        name = devices[device].name
        authors = devices[device].authors
        abstract = devices[device].abstract
        date = devices[device].date
        refs = devices[device].ref_titles
        publisher = devices[device].publisher
        figures = name + '/Figures/'
        sections = name + '/Sections/Sections.txt'
        back_refs = devices[device].back_references
        citations = devices[device].citations

        data = (name, refs, authors, abstract, date, publisher, sections, figures, back_refs, citations)
        values.append(data)

    return values


def find_new_connections(new_devices, cursor):
    devices = get_devices_from_db(cursor)
    updated_db_devices = []
    new_connections = {}

    for new_device in new_devices:
        new_device = new_devices[new_device]
        for device in devices:
            device = DB_Device(device[0], device[1], device[2], device[3], device[4], device[5])
            if new_device.name != device.name:
                connection = find_connection(new_device, device)
                if connection is not None:
                    updated_db_devices.append(device)
                    new_connections[connection.key] = connection

    create_crossrefs(new_connections)
    update_db_devices(updated_db_devices, cursor)
    return new_connections


def update_db_devices(devices, cursor):
    update_db = """
                update prototype_data.publications set refs = %s, citations = %s where id = %s
                """

    for device in devices:
        cursor.execute(update_db, (device.back_references, device.citations, device.id))


def get_devices_from_db(cursor):
    command = "select id, title, authors, all_references, refs, citations from prototype_data.publications"
    cursor.execute(command)
    devices = cursor.fetchall()
    return devices


def find_connection(new_device, device):

    is_cited, times_cited, is_backref = compare_crossrefs(new_device, device)
    shared_authors, shared_refs = find_shared_metadata(new_device, device)

    if is_cited or shared_refs != [] or shared_authors != []:
        if is_backref:
            connection = create_connection(new_device, device, is_cited, times_cited, shared_authors, shared_refs)
        else:
            connection = create_connection(device, new_device, is_cited, times_cited, shared_authors, shared_refs)

        return connection


def find_shared_metadata(new_device, device):
    shared_authors = check_authors(new_device, device)
    shared_references = check_refs(new_device, device)

    return shared_authors, shared_references


def check_refs(new_device, device):
    shared_refs = []
    for ref_0 in new_device.refs:
        for ref_1 in device.refs:
            tol = calculate_tol(ref_0.title, ref_1)
            if tol > 0.75:
                shared_refs.append(ref_1)

        return shared_refs

# checks if new_device cites device
def compare_crossrefs(new_device, device):
    for ref in new_device.refs:
        score = calculate_tol(ref.key, device.key)
        if score > 0.75:
            return True, 1, True

    for ref in device.refs:
        score = calculate_tol(modify_name(ref), new_device.key)
        if score > 0.75:
            return True, 1, False

    return False, 0, False



