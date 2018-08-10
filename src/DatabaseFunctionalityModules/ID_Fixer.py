import psycopg2

get_publications = """
                    select id, title, authors, refs, citations from prototype_data.publications
                   """

get_authors = """
                select id, author_name, publications from prototype_data.authors
              """

update_author = """
                    update prototype_data.authors set publications = %s where id = %s
                """

update_pub = """
                update prototype_data.publications set authors = %s, refs = %s, citations = %s where id = %s
              """


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
        # TODO: can be optimized later
        for pub in pubs:
            # change the name of the publication to the publication id
            author_pubs = [pub[0] if x == pub[1] else x for x in author_pubs]
        value = (author_pubs, author[0])
        cursor.execute(update_author, value)


def update_pubs(pubs, authors, cursor):
    for pub in pubs:
        pub_id = pub[0]
        new_author_list = []
        citations, references = update_crossrefs(pub, pubs)
        for author in authors:
            # if the pub id is in authors pub list, add author id to the new list
            if str(pub_id) in author[2]:
                new_author_list.append(author[0])
        cursor.execute(update_pub, (new_author_list, references, citations, pub_id))


def update_crossrefs(pub, pubs):
    references= pub[3]
    citations = pub[4]
    for publication in pubs:
        citations = [publication[0] if x == publication[1] else x for x in citations]
        references = [publication[0] if x == publication[1] else x for x in references]

    return citations, references
