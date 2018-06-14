import os
import xml.etree.ElementTree as ET

def parsePub(root, device):

    publicationStmt = root.find("{http://www.tei-c.org/ns/1.0}publicationStmt")

    if publicationStmt is not None:
        publisher = publicationStmt.find("{http://www.tei-c.org/ns/1.0}publisher")
        device.publisher(publisher)