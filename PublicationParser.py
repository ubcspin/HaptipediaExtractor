def parsePub(root, device):

    publicationStmt = next(root.iter("{http://www.tei-c.org/ns/1.0}publicationStmt"))

    if publicationStmt is not None:
        publisher = publicationStmt.find("{http://www.tei-c.org/ns/1.0}publisher").text
        if publisher is not None:
            device.publisher = publisher