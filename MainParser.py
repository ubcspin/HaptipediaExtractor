import os
import xml.etree.ElementTree as ET
import json
import SectionParser
import ReferenceParser
from CrossReference import init_device
#import AuthorParser
#import PublicationParser


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

    utf8_paper_title = paper_title.encode('ascii', 'ignore')
    device, device_name = init_device(utf8_paper_title)

    if not os.path.exists(utf8_paper_title):
        os.makedirs(utf8_paper_title)

    os.chdir(utf8_paper_title)

    # TODO: implement once we have tables working
    #AuthorParser.parseAuthor(root)
    #PublicationParser.parsePub(root)
    ReferenceParser.parseReference(root, device)    # creates folder for References
    SectionParser.parseSection(root)        # creates folder for Section Titles and Text
    if not os.path.exists('Figures'):
        os.makedirs('Figures')                  # creates folder for figures
    os.chdir('Figures')
    parse_JSON(JSONfile_path)
    os.chdir('../..')

    return utf8_paper_title


def parse_JSON(file):

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

            with open(figure_number + " Caption.txt", 'w') as caption_text:
                caption_text.write(caption)












