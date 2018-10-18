from DatabaseFunctionalityModules import DatabaseInfo

createPublicationCommand = """create table if not exists """ + DatabaseInfo.pub_table + \
                            """
                                (device varchar,
                                id serial,
                                title varchar,
                                authors text[],
                                all_references json,
                                abstract text,
                                pub_date varchar,
                                publisher varchar,
                                sections varchar,
                                figures varchar,
                                backward_refs json,
                                forward_refs json,
                                shared_authors json,
                                shared_refs json,
                                is_main_pub bool)
                             """

CreateAuthorTableCommand = """
                            create table if not exists 
                            """\
                            + DatabaseInfo.author_table + \
                            """
                            (
                            id serial,
                            author_name varchar,
                            publications text[],
                            affiliations varchar,
                            country varchar)                        
                            """

if __name__ == '__main__':
    connection = DatabaseInfo.connect_to_db()
    cursor = connection.cursor()
    cursor.execute(createPublicationCommand)
    cursor.execute(CreateAuthorTableCommand)
    connection.commit()
    cursor.close()
    connection.close()


    




