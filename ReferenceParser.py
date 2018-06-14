import os
from CrossReference import add_backward_ref, add_forward_ref
import xml.etree.ElementTree as ET

# Parser to extract References from an XML file
# References include:
# 1.) Reference
# 2.) Reference Authors
# 3.) Conference/Journal Published
# 4.) Year it was published
# XML file taken from GROBID API Call
# XML files must be in the same place as this python file
# Output info is temporarily placed in txt file, later will be added to a database


def parseReference(XMLroot, device):

    if not os.path.exists('References'):
        os.makedirs('References')

    os.chdir('References')

    count = 0

    for biblStruct in XMLroot.iter("{http://www.tei-c.org/ns/1.0}biblStruct"):

        if len(biblStruct.attrib.keys()) != 0:  # used to separate paper title from reference titles

            ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}analytic")

            if ref is None:
                # title is either an analytic element or monogr element in the XML File
                ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}monogr")

            try:
                title = ref.find("{http://www.tei-c.org/ns/1.0}title").text

                if title is not None:
                    add_backward_ref(device, title)
                    # add_forward_ref(device, device.name, True, title)

                    count += 1

                    filename = "[" + str(count) + "].txt"

                    with open(filename, "w+", encoding='utf8') as refFile:
                        refFile.write("Title: " + title)
                        writeAuthorsToFile(refFile, ref)
                        writePublishersToFile(title, refFile, biblStruct)

            except Exception as e:
                pass

    for backref in device.forward_ref:
        print(backref)

    os.chdir('..')


def writePublishersToFile(title, refFile, biblStruct):

    pubRef = biblStruct.find("{http://www.tei-c.org/ns/1.0}monogr")
    pubTitle = pubRef.find("{http://www.tei-c.org/ns/1.0}title").text

    if pubTitle is not title:
        refFile.write("\nPublisher: " + pubTitle)

    imprint = pubRef.find("{http://www.tei-c.org/ns/1.0}imprint")

    publisher = imprint.find("{http://www.tei-c.org/ns/1.0}publisher")
    if publisher is not None:
        publisher = publisher.text
        refFile.write(", " + publisher)

    dateElem = imprint.find("{http://www.tei-c.org/ns/1.0}date")
    if dateElem.get('type') == "published":
        date = dateElem.get('when')

    refFile.write("\nDate: " + date)

    for biblScope in imprint.findall("{http://www.tei-c.org/ns/1.0}biblScope"):

        unit = biblScope.get('unit')
        val = biblScope.text

        if unit == 'page':
            refFile.write("\nPages: " + biblScope.get('from') + " to " + biblScope.get('to'))
        elif unit == 'volume':
            refFile.write("\nVolume: " + val)
        elif unit == 'issue':
            refFile.write("\nIssue" + val)



def writeAuthorsToFile(refFile, ref):

    refFile.write("\nAuthors:")

    for author in ref.iter("{http://www.tei-c.org/ns/1.0}author"):
        persName = author.find("{http://www.tei-c.org/ns/1.0}persName")

        try:
            forename = persName.find("{http://www.tei-c.org/ns/1.0}forename")  # doesn't account mid names
            surname = persName.find("{http://www.tei-c.org/ns/1.0}surname")

            if forename is None or surname is None:
                if forename is None:
                    surname = surname.text
                    refFile.write("\n" + surname)

                elif surname is None:
                    forename = forename.text
                    refFile.write("\n" + forename)

            else:
                forename = forename.text
                surname = surname.text
                refFile.write("\n" + surname + ", " + forename)

        except:
            pass


