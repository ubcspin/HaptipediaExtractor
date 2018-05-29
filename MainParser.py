import os
import glob
import xml.etree.ElementTree as ET
import time
import SectionParser
import ReferenceParser

# MainParser that can be called from the commandline
# REQUIRES XML files to be inside a specific folder
# must be in the same directory as the XML files or must be called from main and main puts it in the right directory

forbidden_chars_table = str.maketrans('\/*?:"<>| ', '__________')
start_time = time.time()

def parse_XML(file):

    tree = ET.parse(file)
    root = tree.getroot()

    paper_title = next(root.iter("{http://www.tei-c.org/ns/1.0}title")).text
    print("pre-translation: " + paper_title)
    paper_title = paper_title.translate(forbidden_chars_table)
    print("post-translation: " + paper_title)

    if len(paper_title) > 150:
        paper_title = paper_title[:150]
        paper_title = paper_title + "_"

    utf8_paper_title = paper_title.encode('ascii', 'ignore')

    if not os.path.exists(utf8_paper_title):
        os.makedirs(utf8_paper_title)

    os.chdir(utf8_paper_title)

    ReferenceParser.parseReference(root)
    SectionParser.parseSection(root)

    os.chdir('..')

    return utf8_paper_title










