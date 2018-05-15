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

    parseAbstract(XMLroot)
    parseSectionTitles(XMLroot)

    os.chdir('..')



def parseAbstract(root):

    abstract = next(root.iter("{http://www.tei-c.org/ns/1.0}abstract"))

    try:
        abstract = abstract.find("{http://www.tei-c.org/ns/1.0}p").text

        with open('Abstract.txt', 'w+', encoding='utf8') as abstractFile:
            abstractFile.write(abstract)

    except:
        with open('Abstract.txt', 'w+', encoding='utf8') as abstractFile:
            abstractFile.write("No Abstract")




def parseSectionTitles(root):

    body = next(root.iter("{http://www.tei-c.org/ns/1.0}body"))

    for div in body.iter("{http://www.tei-c.org/ns/1.0}div"):
        section = div.find("{http://www.tei-c.org/ns/1.0}head")

        sectionNumber = section.get('n')
        sectionTitle = section.text
        sectionTitle = sectionTitle.translate(forbidden_chars_table)

        if sectionNumber is not None:

            with open(sectionNumber + " " + sectionTitle + ".txt", 'w+', encoding='utf8') as sectionFile:
                sectionFile.write("Made Section")
        else:
            with open(sectionTitle + ".txt", 'w+', encoding='utf8') as sectionFile:
                sectionFile.write("Made Section")








