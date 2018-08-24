import psycopg2
import json
from Utilities import is_same_author
from DatabaseFunctionalityModules.DatabaseInfo import schema_name

pub_table = schema_name + '.publications'

author_table = schema_name + '.authors'

get_publications = "select id, title, authors, backward_refs, forward_refs, shared_authors, shared_refs from " + pub_table

get_authors = 'select id, author_name, publications from ' + author_table

update_author = 'update ' + author_table + ' set publications = %s where id = %s'

update_pub = 'update ' + pub_table + ' set authors = %s, backward_refs = %s, forward_refs = %s, shared_authors = %s, shared_refs = %s where id = %s'


def fix_pub_and_author_id():
    try:
        # use our connection values to establish a connection
        conn = psycopg2.connect(host='localhost', dbname='testpaperdb', user='postgres', password='postgres',
                                port='5433')
        # create a psycopg2 cursor that can execute queries
        cursor = conn.cursor()
        pubs, authors = get_data(cursor)
        update_authors(pubs, authors, cursor)
        # second call to get_data to fetch new data
        pubs, authors = get_data(cursor)
        update_pubs(pubs, authors, cursor)
        cursor.close()
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def get_data(cursor):
    cursor.execute(get_publications)
    pubs = cursor.fetchall()
    cursor.execute(get_authors)
    authors = cursor.fetchall()

    return pubs, authors


def update_authors(pubs, authors, cursor):
    for author in authors:
        author_pubs = author[2]
        for pub in pubs:
            # change the name of the publication to the publication id
            author_pubs = [pub[0] if x == pub[1] else x for x in author_pubs]
        value = (author_pubs, author[0])
        cursor.execute(update_author, value)


def update_pubs(pubs, authors, cursor):
    for pub in pubs:
        pub_id = pub[0]
        new_author_list = []
        for author in authors:
            # if the pub id is in authors pub list, add author id to the new list
            if str(pub_id) in author[2]:
                new_author_list.append(author[0])
        backward_refs, forward_refs, shared_authors, shared_refs = update_JSONS(pub, authors, pubs)
        cursor.execute(update_pub, (new_author_list, backward_refs, forward_refs, shared_authors, shared_refs, pub_id))


def update_JSONS(pub, authors, pubs):
    backward_refs = pub[3]
    forward_refs = pub[4]
    shared_authors = pub[5]
    shared_refs = pub[6]

    for publication in pubs:
        backward_refs = change_name_to_id(backward_refs, publication)
        forward_refs = change_name_to_id(forward_refs, publication)
        shared_refs = change_name_to_id(shared_refs, publication)

        for author_dict in shared_authors:
            if author_dict['target'] == publication[1]:
                author_dict['target'] = publication[0]
                new_shared_authors = []
                for db_author in authors:
                    #if both pub_id belong to the same author, add the author_id to the list
                    if str(publication[0]) in db_author[2] and str(pub[0]) in db_author[2]:
                        new_shared_authors.append(db_author[0])
                author_dict['shared_authors'] = new_shared_authors

    return json.dumps(backward_refs), json.dumps(forward_refs), json.dumps(shared_authors), json.dumps(shared_refs)


def change_name_to_id(dicts, publication):
    for ref_dict in dicts:
        if ref_dict['target'] == publication[1]:
            ref_dict['target'] = publication[0]

    return dicts


if __name__ == '__main__':
    fix_pub_and_author_id()
