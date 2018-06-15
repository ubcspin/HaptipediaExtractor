import os
import glob
import xml.etree.ElementTree as ET

# Parser to Extract Section Titles and Sections from an XMLfile
# OutputFile is temporarily placed in an output file, later placed into a database
# XML files must be in the same place as this python file
# XML files taken from GROBID API call

# ASSUME: paper already has file for it and we are currently inside it


forbidden_chars_table = str.maketrans('\/*?:"<>|', '_________')


def parseSection(XMLroot, device):

    parse_abstract(XMLroot, device)
    parseSectionTitle(XMLroot, device)

def parse_abstract(root, device):

    abstract = next(root.iter("{http://www.tei-c.org/ns/1.0}abstract"))

    try:
        abstract = abstract.find("{http://www.tei-c.org/ns/1.0}p").text

    except:
        abstract = "No Abstract Extracted"

    device.sections['Abstract'] = abstract


def parseSectionTitle(root, device):

    body = next(root.iter("{http://www.tei-c.org/ns/1.0}body"))

    for div in body.iter("{http://www.tei-c.org/ns/1.0}div"):
        section = div.find("{http://www.tei-c.org/ns/1.0}head")

        sectionNumber = section.get('n')
        sectionTitle = section.text
        sectionTitle = sectionTitle.translate(forbidden_chars_table)

        if sectionNumber is not None:
            section_file = sectionNumber + ' ' + sectionTitle
            # sectionFile = open(sectionNumber + " " + sectionTitle + ".txt", 'a+', encoding='utf8')
        else:
            section_file = sectionTitle
            # sectionFile = open(sectionTitle + ".txt", 'a+', encoding='utf8')

        paragraphs = []

        for paragraph in div.findall("{http://www.tei-c.org/ns/1.0}p"):
            text = paragraph.text
            for ref in paragraph.findall("{http://www.tei-c.org/ns/1.0}ref"):  # extract text after the references
                if ref.tail is not None:
                    text = text + ref.tail

            paragraphs.append(text)

        device.sections[section_file] = paragraphs


