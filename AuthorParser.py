import os
import xml.etree.ElementTree as ET

def parseAuthor(root, device):

    sourceDesc = root.find("{http://www.tei-c.org/ns/1.0}sourceDesc")

    if sourceDesc is not None:
        for author in sourceDesc.iter("{http://www.tei-c.org/ns/1.0}author"):
            persName = author.find("{http://www.tei-c.org/ns/1.0}persName")
            firstName = persName.find("{http://www.tei-c.org/ns/1.0}forename")
            surname = persName.find("{http://www.tei-c.org/ns/1.0}surname")

            if firstName is None:
                firstName = ''

            if surname is None:
                surname = ''

            name = firstName + surname

            if name is not '':
                device.authors.append(name)













