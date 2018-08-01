class Affiliate:
    def __init__(self):
        self.institute = ''
        self.dept = ''
        self.lab = ''


"""
Parser to find a papers authors
root: XMLroot to parse
device: device to add author to
"""
def parseAuthor(root, device):

    sourceDesc = next(root.iter("{http://www.tei-c.org/ns/1.0}sourceDesc"))

    if sourceDesc is not None:
        affiliations = find_affiliations(sourceDesc)
        device.affiliates = affiliations

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


"""
Parser for affiliation of an author
Input:

"""
def find_affiliations(src):
    affiliates = []
    affiliates_elem = src.iter("{http://www.tei-c.org/ns/1.0}affiliation") # gives a list of affiliates
    seen_affiliates = []
    for affiliate in affiliates_elem:
        if 'key' in affiliate.attrib:
            num = affiliate.get('key')
            if num not in seen_affiliates:
                seen_affiliates.append(num)
                orgs = affiliate.findall('{http://www.tei-c.org/ns/1.0}orgName')
                # may have multiple affiliations, dict keeps track which groups belong with each other
                dict = {}
                for org in orgs:
                    type = org.get('type')
                    if 'key' in org.attrib:
                        key = org.get('key')
                        key = key[-1]
                    else:
                        key = '0'
                    val = org.text

                    if key in dict:
                        dict[key].append((type, val))
                    else:
                        dict[key] = [(type, val)]
                for key in dict:
                    new_affl = Affiliate()
                    for type in dict[key]: #gives a list of tuples
                        if type[0] == 'department':
                            dept = type[1]
                            new_affl.dept = dept
                        elif type[0] == 'institution':
                            instit = type[1]
                            new_affl.institute = instit
                        elif type[0] == 'laboratory':
                            lab = type[1]
                            new_affl.lab = lab
                    affiliates.append(new_affl)

    return affiliates

"""
Parser for a papers publication
"""
def parsePub(root, device):

    publicationStmt = next(root.iter("{http://www.tei-c.org/ns/1.0}publicationStmt"))

    if publicationStmt is not None:
        try:
            date = publicationStmt.find("{http://www.tei-c.org/ns/1.0}date").text
            device.date = date
        except:
            pass

        publisher = publicationStmt.find("{http://www.tei-c.org/ns/1.0}publisher").text
        if publisher is not None:
            device.publisher = publisher