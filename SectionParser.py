import os
import glob
import xml.etree.ElementTree as ET
import re

# Parser to Extract Section Titles and Sections from an XMLfile
# OutputFile is temporarily placed in an output file, later placed into a database
# XML files must be in the same place as this python file
# XML files taken from GROBID API call

# ASSUME: paper already has file for it and we are currently inside it


forbidden_chars_table = str.maketrans('\/*?:"<>|', '_________')


def parseSection(XMLroot, device):

    parse_abstract(XMLroot, device)
    cite_vals = parseSectionTitle(XMLroot, device)

    return cite_vals

def parse_abstract(root, device):

    abstract = next(root.iter("{http://www.tei-c.org/ns/1.0}abstract"))

    try:
        abstract = abstract.find("{http://www.tei-c.org/ns/1.0}p").text

    except:
        abstract = "No Abstract Extracted"

    device.sections['Abstract'] = abstract


def parseSectionTitle(root, device):

    body = next(root.iter("{http://www.tei-c.org/ns/1.0}body"))

    cite_occurrence = {}
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

        for paragraph in div.findall("{http://www.tei-c.org/ns/1.0}p"):
            text = paragraph.text
            for ref in paragraph.findall("{http://www.tei-c.org/ns/1.0}ref"):  # extract text after the references
                if ref is not None:
                    attributes = ref.attrib
                    if 'type' in attributes:
                        if attributes['type'] == 'bibr':
                            if 'target' in attributes:
                                ref_number = attributes['target']
                                if ref_number is not None:
                                    ref_number = int(ref_number[2:]) + 1

                                    if ref_number not in cite_occurrence:
                                        cite_occurrence[ref_number] = 1;
                                        print(str(ref_number) + " cited: one time")
                                    else:
                                        val = cite_occurrence[ref_number]
                                        val += 1
                                        cite_occurrence[ref_number] = val
                                        print(str(ref_number) + " cited: %s times" % str(val))

                                    #TODO: fix duplicate code here
                            else:
                                if ref.text is not None:
                                    ref_regex = re.findall(r'\d+', ref.text)
                                    if len(ref_regex) != 0:
                                        ref_number = int(ref_regex[0])

                                        if ref_number not in cite_occurrence:
                                            cite_occurrence[ref_number] = 1;
                                            print(str(ref_number) + " cited: one time")
                                        else:
                                            val = cite_occurrence[ref_number]
                                            val += 1
                                            cite_occurrence[ref_number] = val
                                            print(str(ref_number) + " cited: %s times" % str(val))



                            # TODO: come up with a way to improve the reference counting

                    if ref.tail and ref.text is not None:
                        text = text + ref.text + ref.tail
                    elif ref.text is not None:
                        text = text + ref.text

            paragraphs.append(text)

        device.sections[section_file] = paragraphs

    return cite_occurrence




