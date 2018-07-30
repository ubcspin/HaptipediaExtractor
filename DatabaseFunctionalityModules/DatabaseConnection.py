import psycopg2
from CrossReference import modify_name, calculate_tol, create_connection

"""
Database Schema not finalized yet
"""

"""
Device object that simplifies original device object
"""
class DB_Device:
    def __init__(self, name, authors, refs):
        self.name = name
        self.key = modify_name(name)
        self.authors = authors
        self.refs = refs


def add_data(new_devices, connections):
    new_connections = find_new_connections(new_devices)
    to_add_connections = {**connections, **new_connections}
    add_devices(new_devices)
    add_connections(to_add_connections)


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
    shared_refs = []
    for ref in conn.shared_refs:
        shared_refs.append(ref.title)

    return modify_name(paper_1), paper_1, modify_name(paper_2), paper_2, is_cited, times_cited, shared_authors, shared_refs


def add_devices(new_devices):
    values = create_values(new_devices)
    command = """
                    INSERT INTO papers(paperID, name, date,authors, refs, publisher, figures, section, pdf_name)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    """

    try:
        # use our connection values to establish a connection
        conn = psycopg2.connect(host='localhost', dbname='testpaperdb', user='postgres', password='postgres',
                                port='5433')
        # create a psycopg2 cursor that can execute queries
        cursor = conn.cursor()

        for value in values:
            try:
                cursor.execute(command, value)
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


def create_values(devices):
    values = []
    for device in devices:
        paperID = devices[device].key
        name = devices[device].name
        authors = devices[device].authors
        date = devices[device].date
        refs = devices[device].backward_ref_titles
        publisher = devices[device].publisher
        figures = name + '/Figures/'
        sections = name + '/Sections/Sections.txt'
        pdf_name = devices[device].pdf

        data = (paperID, name, date, authors, refs, publisher, figures, sections, pdf_name)
        values.append(data)

    return values


def find_new_connections(new_devices):

    devices = get_devices_from_db()
    new_connections = {}

    for new_device in new_devices:
        new_device = new_devices[new_device]
        for device in devices:
            device = DB_Device(device[0], device[1], device[2])
            if new_device.name != device.name:
                connection = check_connection(new_device, device)
                if connection is not None:
                    new_connections[connection.key] = connection

    return new_connections


def get_devices_from_db():
    command = "select name, authors, refs from papers"

    try:
        # use our connection values to establish a connection
        conn = psycopg2.connect(host='localhost', dbname='testpaperdb', user='postgres', password='postgres',
                                port='5433')
        # create a psycopg2 cursor that can execute queries
        cursor = conn.cursor()
        cursor.execute(command)
        devices = cursor.fetchall()
        cursor.close()
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()

    return devices


def check_connection(new_device, device):

    is_cited, times_cited, is_backref = check_crossref(new_device, device)
    shared_authors, shared_refs = find_shared_metadata(new_device, device)

    if is_cited or shared_refs != [] or shared_authors != []:
        if is_backref:
            connection = create_connection(new_device, device, is_cited, times_cited, shared_authors, shared_refs)
        else:
            connection = create_connection(device, new_device, is_cited, times_cited, shared_authors, shared_refs)

        return connection


# checks if new_device cites device
def check_crossref(new_device, device):
    for ref in new_device.backward_ref:
        score = calculate_tol(ref.key, device.key)
        if score > 0.75:
            return True, 1, True

    for ref in device.refs:
        score = calculate_tol(modify_name(ref), new_device.key)
        if score > 0.75:
            return True, 1, False

    return False, 0, False


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
        for ref2 in device2.refs:
            tol = calculate_tol(modify_name(ref1.title), modify_name(ref2))
            if tol > 0.75:
                shared_refs.append(ref1)

    return shared_refs



