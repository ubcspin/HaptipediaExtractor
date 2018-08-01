import os
import xml.etree.ElementTree as ET
import SectionParser
import ReferenceParser
from MetaDataParser import parseAuthor, parsePub
from Device import init_device, update_name


forbidden_chars_table = str.maketrans('\/*?:"<>|', '_________')

"""
Calls the different parsers to extract information from XML files. Creates a folder to hold the figures
and the figure captions.
"""

def parse_file(XMLfile_path, pdf_name):

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

    device, device_key = init_device(paper_title, pdf_name)

    # call all the needed parsers to extract data from XML file
    parseAuthor(root, device)
    parsePub(root, device)
    cite_vals, citation_placements, unaccounted_citations = SectionParser.parseSection(root, device)
    ReferenceParser.parseReference(root, device, cite_vals, citation_placements, unaccounted_citations)

    if not os.path.exists(paper_title):
        os.makedirs(paper_title)
    else: # for some reason the name already exists then
        paper_title = fix_same_title(device, paper_title)

    os.chdir(paper_title)
    if not os.path.exists('Figures'):
        os.makedirs('Figures')
    os.chdir('..')

    return paper_title


"""
Method in case if two papers titles were extracted incorrectly and are the same,
changes the name by first checking the year of the paper, if not available,
then rename the paper with paper_name(count)
"""


def fix_same_title(device, paper_title):
    if device.date is not '':
        date_title = paper_title + "(" + device.date + ")"
        if os.path.exists(date_title):
            count = 1
            new_title = date_title
            while os.path.exists(new_title):
                new_title = date_title + '(' + str(count) + ')'
                count += 1
            update_name(new_title, device)
            os.makedirs(new_title)
            return new_title
        else:
            update_name(date_title, device)
            os.makedirs(date_title)
            return date_title

    else:
        count = 1
        new_title = paper_title
        while os.path.exists(new_title):
            new_title = paper_title + '(' + str(count) + ')'
            count += 1

        os.makedirs(new_title)
        update_name(new_title, device)
        return new_title

