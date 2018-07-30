import psycopg2
from CrossReference import modify_name, calculate_tol, create_connection, find_shared_metadata

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
    shared_refs = conn.shared_refs

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
            #try:
            cursor.execute(command, value)
            # except Exception as e:
            #     print(e)
            #     pass
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
        refs = devices[device].refs
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
                connection = find_connection(new_device, device)
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


def find_connection(new_device, device):

    is_cited, times_cited, is_backref = compare_crossrefs(new_device, device)
    shared_authors, shared_refs = find_shared_metadata(new_device, device)

    if is_cited or shared_refs != [] or shared_authors != []:
        if is_backref:
            connection = create_connection(new_device, device, is_cited, times_cited, shared_authors, shared_refs)
        else:
            connection = create_connection(device, new_device, is_cited, times_cited, shared_authors, shared_refs)

        return connection


# checks if new_device cites device
def compare_crossrefs(new_device, device):
    for ref in new_device.backward_ref:
        score = calculate_tol(ref.key, device.key)
        if score > 0.75:
            return True, 1, True

    for ref in device.refs:
        score = calculate_tol(modify_name(ref), new_device.key)
        if score > 0.75:
            return True, 1, False

    return False, 0, False



