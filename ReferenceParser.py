import os
import glob
import xml.etree.ElementTree as ET

# Parser to extract References from an XML file
# References include:
# 1.) Reference Title
# 2.) Reference Authors
# 3.) Conference/Journal Published
# 4.) Year it was published
# 5.) Plus More!!!
# XML file taken from GROBID API Call

forbidden_chars_table = str.maketrans('\/*?:"<>|', '_________')


def parseReference(XMLFile):
    tree = ET.parse(XMLFile)
    root = tree.getroot()

    paper_title = next(root.iter("{http://www.tei-c.org/ns/1.0}title")).text
    print("pre-translation: " + paper_title)
    paper_title = paper_title.translate(forbidden_chars_table)
    print("post-translation: " + paper_title)

    if len(paper_title) > 150:
        paper_title = paper_title[:150]
        paper_title = paper_title + "_"

    utf8_paper_title = paper_title.encode('ascii', 'ignore')

    if not os.path.exists(utf8_paper_title):  # should be later changed to name of the paper
        os.makedirs(utf8_paper_title)

    os.chdir(utf8_paper_title)

    if not os.path.exists('References'):
        os.makedirs('References')

    os.chdir('References')

    for biblStruct in root.iter("{http://www.tei-c.org/ns/1.0}biblStruct"):

        if len(biblStruct.attrib.keys()) != 0:   # used to separate paper title from reference titles

            ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}analytic")

            for author in ref.iter("{http://www.tei-c.org/ns/1.0}author"):
                persName = author.find("{http://www.tei-c.org/ns/1.0}persName")
                forename = persName.find("{http://www.tei-c.org/ns/1.0}forename").text # doesn't take care of middle names
                surname = persName.find("{http://www.tei-c.org/ns/1.0}surname").text

                print(forename + "." + surname)

            if ref is None:
                # title is either an analytic element or monogr element in the XML File
                ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}monogr")

            title = ref.find("{http://www.tei-c.org/ns/1.0}title").text
            print(title)

            global count
            count += 1

            createRefFile(title, count)


    os.chdir('..')


def createRefFile(title, count):

    filename = "[" + str(count) + "].txt"

    with open(filename, "w+", encoding='utf8') as refFile:
        refFile.write("Title: " + title)





for file in glob.glob("*.xml"):
    count = 0
    parseReference(file)
    print(count)