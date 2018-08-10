import os
import csv


def writeFiles(devices, connections, authors):

    write_connections(connections)
    write_authors(authors)
    # write_cite_dist(devices, connections)
    write_PDF_tracker(devices)

    for device in devices:
        device = devices[device]
        os.chdir(device.name)

        write_metadata(device)
        write_sections(device)
        write_references(device)

        os.chdir('..')


def write_authors(authors):
    with open("Author List.txt", 'w+', encoding='utf8') as file:
        for author in authors:
            file.write(author.name + "\nPublications:\n")
            for pub in author.publications:
                file.write(pub + '\n')


def write_scores(connections_to_check):
    with open("Scores_To_Check.txt", 'w+', encoding='utf8') as file:
        for conn in connections_to_check:
            file.write(conn + '\n')


def write_PDF_tracker(devices):
    with open("PDF_Names_and_Titles.txt", 'w+', encoding='utf8') as file:
        for device in devices:
            file.write('Data from %s is in %s\n' % (devices[device].pdf, devices[device].name))


def write_connections(connections):
    if connections is not None:
        with open("Cross References.txt", 'w+', encoding='utf8') as file:
            for connection in connections:
                conn = connections[connection]
                if conn.is_cited:
                    file.write ('\n%s referenced %s (Cited %s times)\n' % (conn.device.name, conn.connected_device.name, conn.times_cited))
                else:
                    file.write('\n%s connected to %s\n' %(conn.device.name, conn.connected_device.name))
                file.write('Shared Authors:\n')
                if conn.shared_authors != []:
                    for author in conn.shared_authors:
                        file.write(author + '\n')
                file.write('Shared References:\n')
                if conn.shared_refs != []:
                    for ref in conn.shared_refs:
                        file.write(ref.title + '\n')

        print(len(connections))


def write_metadata(device):
    with open("Authors.txt", 'w+', encoding='utf8') as file:
        if device.authors is not []:
            for author in device.authors:
                file.write(author + '\n')
        else:
            file.write("No Authors Extracted")

    with open("Affiliations.txt", 'w+', encoding='utf8') as file:
        if device.affiliates is not []:
            for affiliate in device.affiliates:
                file.write('Laboratory: %s\n' % affiliate.lab)
                file.write('Department: %s\n' % affiliate.dept)
                file.write('Institution: %s\n\n' % affiliate.institute)

    with open("Publisher.txt", 'w+', encoding='utf8') as file:
        if device.publisher != '':
            file.write(device.publisher)
        else:
            file.write("No Publisher Extracted")


def write_sections(device):
    if not os.path.exists('Sections'):
        os.makedirs('Sections')
    os.chdir('Sections')

    write_abstract(device)
    try:
        with open('Sections.txt', 'w+', encoding='utf8') as file:
            for section in device.sections:
                file.write(section + '\n' + '\n')

                for paragraph in device.sections[section]:
                    file.write(paragraph)

                file.write('\n' + '\n')
    except:
        pass

    os.chdir('..')


def write_abstract(device):
    with open('Abstract.txt', 'w+', encoding='utf8') as file:
        file.write(device.sections['Abstract'])


def write_figures(device):
    os.chdir('Figures')
    for figure_number in device.figures:
        figure_caption = device.figures[figure_number]
        try:
            with open(figure_number + '.txt', 'w+', encoding='utf8') as file:
                file.write(figure_caption)
        except:
            pass
    os.chdir('..')


def write_references(device):
    if not os.path.exists('References'):
        os.makedirs('References')
    os.chdir('References')
    for reference in device.refs:
        with open("[" + str(reference.refNumber) + "].txt", 'w+', encoding='utf8') as file:
            file.write('Title: ' + reference.title + '\n')
            file.write('Authors:\n')
            for author in reference.authors:
                file.write(author + '\n')
            publisher = reference.publisher
            if publisher is not None:
                file.write('Publisher: ' + publisher['name'] + '\n')
                file.write('Date: ' + publisher['date'] + '\n')
                file.write('Page: ' + publisher['pages'] + '\n')
                file.write('Volume: ' + publisher['volume'] + '\n')
                file.write('Issue: ' + publisher['issue'] + '\n')
                file.write('Times Cited: ' + str(reference.timesCited) + '\n')
                file.write('Location in Text Cited:\n')
                for location in reference.locations_cited:
                    file.write(location + '\n')

    os.chdir('..')


# def write_cite_dist(devices, connections):
#     dist = {}
#     number_ref = 0
#     # for connection in connections:
#     #     key = connection.times_cited
#     #     if key in dist:
#     #         dist[key] = dist[key] + 1
#     #     else:
#     #         dist[key] = 1
#
#     with open('Outliers.txt', 'w+') as file:
#         for device in devices:
#             for citation in devices[device].backward_ref:
#                 number_ref += 1
#                 key = citation.timesCited
#                 if key > 4:
#                     file.write(devices[device].name + ' cited ' + citation.title + ' ' + str(key) + ' times\n')
#                 if key in dist:
#                     dist[key] = dist[key] + 1
#                 else:
#                     dist[key] = 1
#
#     with open('Distribution.csv', 'w+', newline='') as file:
#         fieldnames = ['times_cited', 'occurance']
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         writer.writeheader()
#         for key in sorted(dist):
#             writer.writerow({'times_cited': key, 'occurance': dist[key]})


# def write_forward_refs(device, devices):
#     with open("Papers That Cited This Paper.txt", 'w+', encoding='utf8') as file:
#         for ref in device.forward_ref:
#             forward_ref = devices[ref]
#             file.write(forward_ref.title + "AND CITED " + str(forward_ref.timesCited) + " TIMES" + '\n')













