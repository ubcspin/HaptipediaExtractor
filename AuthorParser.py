def parseAuthor(root, device):

    sourceDesc = next(root.iter("{http://www.tei-c.org/ns/1.0}sourceDesc"))

    if sourceDesc is not None:
        for author in sourceDesc.iter("{http://www.tei-c.org/ns/1.0}author"):
            persName = author.find("{http://www.tei-c.org/ns/1.0}persName")
            if persName is not None:
                firstName = persName.find("{http://www.tei-c.org/ns/1.0}forename")
                surname = persName.find("{http://www.tei-c.org/ns/1.0}surname")

                if firstName is not None and surname is not None:
                    if len(firstName.text) == 1:
                        name = firstName.text + ". " + surname.text
                    else:
                        name = firstName.text + " " + surname.text

                else:
                    if surname is not None:
                        name = surname.text

                    else:
                        name = ''

                if name is not '':
                    device.authors.append(name)














