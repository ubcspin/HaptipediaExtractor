import os


def writeFiles(devices):
    for device in devices:
        device = devices[device]
        os.chdir(device.name)

        write_metadata(device)
        write_sections(device)
        write_figures(device)
        write_references(device)

        os.chdir('..')


def write_metadata(device):
    with open("Authors.txt", 'w+', encoding='utf8') as file:
        if device.authors is not []:
            for author in device.authors:
                file.write(author + '\n')
        else:
            file.write("No Authors Extracted")

    with open("Publisher.txt", 'w+', encoding='utf8') as file:
        if device.publisher != '':
            file.write(device.publisher)
        else:
            file.write("No Publisher Extracted")


def write_sections(device):
    if not os.path.exists('Sections'):
        os.makedirs('Sections')
    os.chdir('Sections')
    for section in device.sections:
        if section == 'Abstract':
            with open('Abstract.txt', 'w+', encoding='utf8') as file:
                file.write(device.sections[section])
        else:
            with open(section + '.txt', 'w+', encoding='utf8') as file:
                for paragraph in device.sections[section]:
                    file.write(paragraph + '\n')

    os.chdir('..')


def write_figures(device):
    os.chdir('Figures')
    for figure_number in device.figures:
        figure_caption = device.figures[figure_number]
        with open(figure_number + '.txt', 'w+', encoding='utf8') as file:
            file.write(figure_caption)
    os.chdir('..')


def write_references(device):
    if not os.path.exists('References'):
        os.makedirs('References')
    os.chdir('References')
    for citation in device.citations:
        with open("[" + str(citation.refNumber) + "].txt", 'w+', encoding='utf8') as file:
            file.write('Title: ' + citation.title + '\n')
            file.write('Authors:\n')
            for author in citation.authors:
                file.write(author + '\n')
            publisher = citation.publisher
            if publisher.name is not None:
                file.write('Publisher: ' + publisher.name + '\n')
            file.write('Date: ' + publisher.date + '\n')
            file.write('Page: ' + publisher.page + '\n')
            file.write('Volume: ' + publisher.volume + '\n')
            file.write('Issue: ' + publisher.date + '\n')

    os.chdir('..')











