import os
import xml.etree.ElementTree as ET
import json
import SectionParser
import ReferenceParser
from MetaDataParser import parseAuthor, parsePub
from Device import init_device, update_key


# MainParser that can be called from the commandline
# REQUIRES XML files to be inside a specific folder
# must be in the same directory as the XML files or must be called from main and main puts it in the right directory

forbidden_chars_table = str.maketrans('\/*?:"<>|', '_________')


def parse_files(XMLfile_path, JSONfile_path):

    tree = ET.parse(XMLfile_path)
    root = tree.getroot()

    paper_title = next(root.iter("{http://www.tei-c.org/ns/1.0}title")).text
    if paper_title is not None:
        print("pre-translation: " + paper_title)
        paper_title = paper_title.translate(forbidden_chars_table)
        print("post-translation: " + paper_title)
    else:
        paper_title = XMLfile_path[:-4]

    if len(paper_title) > 150:
        paper_title = paper_title[:150]
        paper_title = paper_title + "_"

    if type(paper_title) is not str:
        paper_title = str(paper_title, 'utf8')

    device, device_key = init_device(paper_title)

    parseAuthor(root, device)
    parsePub(root, device)
    cite_vals = SectionParser.parseSection(root, device)
    ReferenceParser.parseReference(root, device, cite_vals)
    parse_JSON(JSONfile_path, device)

    if not os.path.exists(paper_title):
        os.makedirs(paper_title)
    else: # for some reason folder already exists then
        if device.date is not '':
            paper_title = paper_title + "(" + device.date + ')'
            device.name = paper_title
            update_key(device.date, device_key)

            os.makedirs(paper_title)
        else:
            paper_title = paper_title + '(1)'
            device.name = paper_title
            # what are the chances of 3 papers having the same name?
            os.makedirs(paper_title)

    os.chdir(paper_title)
    if not os.path.exists('Figures'):
        os.makedirs('Figures')
    os.chdir('..')

    return paper_title


def parse_JSON(file, device):

    try:
        with open(file, 'r') as json_file:
            data = json.load(json_file)

            for x in range(len(data)):
                caption = data[x]["caption"]
                figType = data[x]["figType"]
                number = data[x]['name']

                figure_number = number

                if figType == 'Figure':
                    figure_number = "Figure " + number
                elif figType == 'Table':
                    figure_number = 'Table ' + number

                device.figures[figure_number] = caption
    except:
        print("No JSON found for " + file)











