import os
import glob
import string
import xml.etree.ElementTree as ET

# Parser to extract References from an XML file
# References include:
# 1.) Reference Title
# 2.) Reference Authors
# 3.) Conference/Journal Published
# 4.) Year it was published
# 5.) Plus More!!!
# XML file taken from GROBID API Call


forbidden_chars_table = string.maketrans('\/*?:"<>|', '_________')


def parseReference(XMLFile):
    tree = ET.parse(XMLFile)
    root = tree.getroot()

    #paper_title = next(root.iter("{http://www.tei-c.org/ns/1.0}title")).text
    #paper_title = paper_title.translate(forbidden_chars_table)

    if not os.path.exists('test'):  # should be later changed to name of the paper
        os.makedirs('test')

    os.chdir('test')

    if not os.path.exists('References'):
        os.makedirs('References')

    os.chdir('References')

    for biblStruct in root.iter("{http://www.tei-c.org/ns/1.0}biblStruct"):

        if len(biblStruct.attrib.keys()) != 0:   # used to separate paper title from reference titles

            ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}analytic")

            if ref is None:
                # title is either in analytic element or monogr element
                ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}monogr")


            title = ref.find("{http://www.tei-c.org/ns/1.0}title").text
            title.translate(forbidden_chars_table)
            print title


            global count
            count += 1

            # createRefFile(title, count)


def createRefFile(title, count):

    with open("[" + str(count) + "] " + title + ".txt", 'w') as refFile:
        refFile.write("Title: " + title)



for file in glob.glob("*.xml"):
    count = 0
    parseReference(file)
    print count


