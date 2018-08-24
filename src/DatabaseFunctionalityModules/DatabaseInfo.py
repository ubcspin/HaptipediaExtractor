import psycopg2
import json

schema_name = 'public'
pub_table = schema_name + '.publications'
author_table = schema_name + '.authors'

test_json = json.dumps([{'target': 0, 'times_cited': 0}])

pub_val = ('foo', test_json, ['4', '5'], '', '1998', 'bar', 'foo/sections.txt',
                'foo/figures/', test_json , test_json, test_json, test_json)

author_val = ('smith', [])


def connect_to_db():
    try:
        conn = psycopg2.connect(host='localhost', dbname='testpaperdb', user='postgres', password='postgres', port='5433')
        return conn
    except Exception as e:
        print(e)
        return None


def check_table(cursor):

    pub_column_test = 'select id, device, title, all_references, authors, abstract, pub_date, publisher, sections,' \
                      ' figures, backward_refs, forward_refs, shared_authors, shared_refs from ' + schema_name + '.publications'

    author_column_test = 'select id, author_name, publications from ' + schema_name + '.authors'

    pub_val_test = 'insert into ' + schema_name + '.publications (title, all_references, authors, abstract, pub_date, '\
                    'publisher, sections, figures, backward_refs, forward_refs, shared_authors, shared_refs)' \
                    'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

    author_val_test = 'insert into ' + schema_name + '.authors (author_name, publications) values (%s, %s)'

    try:
        cursor.execute(pub_column_test)
        cursor.execute(pub_val_test, pub_val)
    except Exception as e:
        print(e)
        print('Publication Table Columns have incorrect name or types, see documents for correct column names')
        return False

    try:
        cursor.execute(author_column_test)
        cursor.execute(author_val_test, author_val)
    except Exception as e:
        print(e)
        print('Authors Table Columns have incorrect name or types, see documents for correct column names')
        return False

    return True















