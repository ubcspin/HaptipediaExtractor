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
        else:
            section_file = sectionTitle

        paragraphs = []
        cite_occurrence = {}

        for paragraph in div.findall("{http://www.tei-c.org/ns/1.0}p"):
            text = paragraph.text
            for ref in paragraph.findall("{http://www.tei-c.org/ns/1.0}ref"):  # extract text after the references
                if ref is not None:
                    attributes = ref.attrib
                    if 'type' in attributes:
                        if attributes['type'] is 'bibr':
                            ref_number = attributes['target']
                            ref_number = int(ref_number[2:]) + 1
                            if ref_number not in cite_occurrence:
                                cite_occurrence[ref_number] = 0;
                            else:
                                val = cite_occurrence[ref_number]
                                cite_occurrence[ref_number] = ++val

                    if ref.tail is not None:

                        text = text + ref.text + ref.tail
                    else:
                        text = text + ref.text

            paragraphs.append(text)

        device.sections[section_file] = paragraphs


