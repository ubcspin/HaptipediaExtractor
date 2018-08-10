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
    cite_vals = parse_and_find_citation_vals(XMLroot, device)

    return cite_vals


def parse_abstract(root, device):

    abstract = next(root.iter("{http://www.tei-c.org/ns/1.0}abstract"))

    try:
        abstract = abstract.find("{http://www.tei-c.org/ns/1.0}p").text

    except:
        abstract = "No Abstract Extracted"

    device.sections['Abstract'] = abstract
    device.abstract = abstract

"""
Parses through section to extract text and also counts number of times each citation is cited and where it was cited
Outputs:
cite_occurance: for each citation, gives the number of times it was cited in the text
citation_placement: for each citation, give the sections where it was cited
unaccounted_citations: 
"""

def parse_and_find_citation_vals(root, device):

    body = next(root.iter("{http://www.tei-c.org/ns/1.0}body"))

    cite_occurrence = {}
    citation_placement = {}
    citations_not_accounted = []
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
                    extract_ref_count(ref, cite_occurrence, citation_placement, citations_not_accounted, section_file)
                    if ref.tail and ref.text is not None:
                        text = text + ref.text + ref.tail
                    elif ref.text is not None:
                        text = text + ref.text

            paragraphs.append(text)

        if section_file in device.sections:
            count = 1
            section_file = section_file + '(1)'
            while section_file in device.sections:
                count += 1
                section_file = section_file[:-3] + '(' + str(count) + ')'

        device.sections[section_file] = paragraphs

    return cite_occurrence, citation_placement, citations_not_accounted


def extract_ref_count(ref, cite_occurrence, citation_placement, citations_not_accounted, section_file):
    attributes = ref.attrib
    if ref.text is not None:
        if 'type' in attributes:
            if attributes['type'] == 'bibr':
                """
                    if ref_regex has only one item, then the text is either [/d/d?] or (/d/d?)
                    if not, then the text in the form (Author Name, \d\d\d\d)
                """
                if 'target' in attributes:
                    bibr_number = attributes['target']
                    if bibr_number is not None:
                        bibr_number = int(bibr_number[2:])
                        ref_regex = re.findall(r'\d\d?', ref.text)

                        if len(ref_regex) == 1:
                            ref_number = compare_ref_numbers(bibr_number, int(ref_regex[0]))
                        else:
                            # if our citation in the form of (Author Name, \d\d\d\d), assume the bibr number is correct
                            ref_number = bibr_number + 1
                        add_ref_count(ref_number, cite_occurrence, citation_placement, section_file)

                else:
                    ref_regex = re.findall(r'\d\d?', ref.text)
                    if len(ref_regex) == 1:
                        # conditional to stop equation references added to ref-count
                        if '(' not in ref.text and ')' not in ref.text:
                            ref_number = int(ref_regex[0])
                            add_ref_count(ref_number, cite_occurrence, citation_placement, section_file)
                    else:
                        # if GROBID can't match reference, add to citations_not_accounted,
                        # citations_not_accounted is a list of tuples with the ref text and the section it was cited in
                        citations_not_accounted.append((ref.text, section_file))


def compare_ref_numbers(bibr_number, text_number):
    # Correct format: bibr_number + 1 == text_number
    if (text_number - bibr_number) == 1:
        return bibr_number + 1
    else:
        # if not in the right format, default to the number in the text
        return text_number


def add_ref_count(ref_number, cite_occurrence, citation_locations, section_file):
    if ref_number not in cite_occurrence:
        cite_occurrence[ref_number] = 1;
        citation_locations[ref_number] = [section_file]
        print(str(ref_number) + " cited: one time")

    else:
        cite_occurrence[ref_number] += 1
        if section_file not in citation_locations[ref_number]:
            citation_locations[ref_number].append(section_file)
        print(str(ref_number) + " cited: %s times" % str(cite_occurrence[ref_number]))








