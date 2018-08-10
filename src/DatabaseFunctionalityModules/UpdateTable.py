from CrossReference import calculate_tol, modify_name, create_connection
from DatabaseConnection import DB_Device, get_devices_from_db, add_connections
import psycopg2

"""
Database schema not finalized, may still be changed.
"""


def update_tables(old_name, new_name):
    try:
        # use our connection values to establish a connection
        conn = psycopg2.connect(host='localhost', dbname='testpaperdb', user='postgres', password='postgres',
                                port='5433')
        # create a psycopg2 cursor that can execute queries
        cursor = conn.cursor()

        try:
            device = get_specific_device(old_name, cursor)
            device = DB_Device(device[0], new_name, device[2], device[3], device[4], device[5])
            devices = get_devices_from_db()
            possible_connections = check_new_connections(device, devices)
            print(possible_connections)
            update_rows(old_name, new_name, cursor, possible_connections)
            # add_connections(possible_connections, device.key, cursor)
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


def add_connections(possible_connections, new_name, cursor):
    curr_connections = get_existing_connections(new_name, cursor) #should return tuples of connections

    for connection in possible_connections:
        # check if there's an entry for shared metadata in the write order
        if (connection[2], connection[3]) in curr_connections:
            update_connection(True, connection[2], connection[3], cursor)
        # check if there's a shared metadata connection but in the wrong order
        elif (connection[3], connection[2]) in curr_connections:
            update_connection(False, connection[3], connection[2], cursor)
        # connection doesn't exist so we need to create one
        else:
            create_new_connection(cursor, connection)


def create_new_connection(cursor, connection):
    command = """insert into connections(paper_1id, paper_1, paper_2id, paper_2, is_cited, times_cited, shared_authors,
                shared_refs) values (%s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (connection[2], connection[0], connection[3], connection[1], True, 1, [], [])
    cursor.execute(command, values)


def update_connection(in_right_order, paper_1id, paper_2id, cursor):
    if in_right_order:
        command = "update connections set is_cited = %s where paper_1id = %s and paper_2id = %s"
        values = (True, paper_1id, paper_2id)
        cursor.execute(command, values)
    else:
        command = "select paper_1, paper_2 from connections where paper_1id = %s and paper_2id = %s"
        values = (paper_1id, paper_2id)
        cursor.execute(command, values)
        data = cursor.fetchone()
        update_comm = """ update connections set paper_1 = %s, paper_1id = %s, is_cited = %s, paper_2 = %s, paper_2id = %s
                        where paper_1id = %s and paper_2id = %s """
        values = (data[1], paper_2id, True, data[0], paper_1id, paper_1id, paper_2id)
        cursor.execute(update_comm, values)


def get_existing_connections(new_name, cursor):
    curr_connections = []
    comm = """select paper_1id, paper_2id from connections
                where (paper_1id = %s and is_cited = '%s') or (paper_2id = %s) """

    cursor.execute(comm, [new_name, False, new_name])
    curr_connections = cursor.fetchall()
    print(curr_connections)
    return curr_connections


def update_rows(old_name, new_name, cursor, new_connections):
    update_comm = "update prototype_data.publications set title = %s where title = %s"
    values = (new_name, old_name)
    cursor.execute(update_comm, values)

    for connection in new_connections:
        updated_publication = connection[3]
        publication = connection[2]

        update_crossref(publication, updated_publication, cursor)

    # update_connections_0 = "update connections set paper_1 = %s where paper_1 = %s"
    # update_connections_1 = "update connections set paper_2 = %s where paper_2 = %s"
    # values = (new_name, old_name)
    # cursor.execute(update_connections_0, values)
    # cursor.execute(update_connections_1, values)


def update_crossref(publication, updated_publication, cursor):
    get_refs = "select refs from prototype_data.publications where id = %s"
    get_citations = "select citations from prototype_data.publications where id = %s"

    update_refs = "update prototype_data.publications set refs = %s where id = %s"
    update_citations = "update prototype_data.publications set citations = %s where id = %s"

    cursor.execute(get_refs, (publication.id,))
    refs = cursor.fetchone()

    cursor.execute(get_citations, (updated_publication.id, ))
    citations = cursor.fetchone()

    print(type(refs))
    print(type(citations))

    refs.append(updated_publication.id)
    citations.append(publication.id)

    cursor.execute(update_refs, (publication.id, refs))
    cursor.execute(update_citations, (updated_publication.id, citations))


def get_specific_device(old_name, cursor):
    command = "select id, title, authors, all_references, refs, citations from prototype_data.publications where title = %s"
    cursor.execute(command, (old_name, ))
    device = cursor.fetchone()
    return device


def check_new_connections(updated_device, devices):
    possible_connections = [] # list of tuples of devices that referenced this device
    for device in devices:
        device = DB_Device(device[0], device[1], device[2], device[3], device[4], device[5])
        for ref in device.refs:
            tol = calculate_tol(updated_device.key, modify_name(ref))
            if tol > 0.75:
                possible_connections.append((device.id, updated_device.id, device, updated_device))

    return possible_connections


if __name__ == '__main__':
    update_tables('07463158', 'A Robotic Touchscreen Totem for Two-Dimensional Haptic Force Display')