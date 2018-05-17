import os
import glob
import xml.etree.ElementTree as ET

# Parser to Extract Section Titles and Sections from an XMLfile
# OutputFile is temporarily placed in an output file, later placed into a database
# XML files must be in the same place as this python file
# XML files taken from GROBID API call

# ASSUME: paper already has file for it and we are currently inside it


forbidden_chars_table = str.maketrans('\/*?:"<>|', '_________')


def parseSection(XMLroot):

    if not os.path.exists('Sections'):
        os.makedirs('Sections')

    os.chdir('Sections')

    parse_abstract(XMLroot)
    parseSectionTitle(XMLroot)

    os.chdir('..')


def parse_abstract(root):

    abstract = next(root.iter("{http://www.tei-c.org/ns/1.0}abstract"))

    try:
        abstract = abstract.find("{http://www.tei-c.org/ns/1.0}p").text

        with open('Abstract.txt', 'w+', encoding='utf8') as abstractFile:
            abstractFile.write(abstract)

    except:
        with open('Abstract.txt', 'w+', encoding='utf8') as abstractFile:
            abstractFile.write("No Abstract")


def parseSectionTitle(root):

    body = next(root.iter("{http://www.tei-c.org/ns/1.0}body"))

    for div in body.iter("{http://www.tei-c.org/ns/1.0}div"):
        section = div.find("{http://www.tei-c.org/ns/1.0}head")

        sectionNumber = section.get('n')
        sectionTitle = section.text
        sectionTitle = sectionTitle.translate(forbidden_chars_table)

        if sectionNumber is not None:
            sectionFile = open(sectionNumber + " " + sectionTitle + ".txt", 'a+', encoding='utf8')
        else:
            sectionFile = open(sectionTitle + ".txt", 'a+', encoding='utf8')

        for paragraph in div.findall("{http://www.tei-c.org/ns/1.0}p"):
            text = paragraph.text
            for ref in paragraph.findall("{http://www.tei-c.org/ns/1.0}ref"):  # extract text after the references
                if ref.tail is not None:
                    text = text + ref.tail
            sectionFile.write(text + "\n")

        sectionFile.close()


