from CrossReference import modify_name

# Parser to extract References from an XML file
# References include:
# 1.) Reference
# 2.) Reference Authors
# 3.) Conference/Journal Published
# 4.) Year it was published
# XML files must be in the same place as this python file
# Output info is temporarily placed in txt file, later will be added to a database


class Reference:
    def __init__(self, title, refNumber):
        self.refNumber = refNumber
        self.title = title
        self.key = modify_name(title)
        self.authors = []
        self.publisher = Publisher()
        self.timesCited = 1


class Publisher:
    def __init__(self):
        self.name = ''
        self.date = ''
        self.page = ''
        self.volume = ''
        self.issue = ''


def parseReference(XMLroot, device, cite_vals):

    count = 1

    ref_root = next(XMLroot.iter("{http://www.tei-c.org/ns/1.0}listBibl"))

    for biblStruct in ref_root.iter("{http://www.tei-c.org/ns/1.0}biblStruct"):

        if len(biblStruct.attrib.keys()) != 0:  # used to separate paper title from reference titles

            ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}analytic")

            if ref is None:
                # title is either an analytic element or monogr element in the XML File
                ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}monogr")


            try:
                title = ref.find("{http://www.tei-c.org/ns/1.0}title").text

                if title is not None:
                    reference = Reference(title, count)

                    try:
                        writeAuthors(ref, reference)
                    except:
                        print("problem writing authors")
                    try:
                        writePublishers(title, biblStruct, reference)
                        if count in cite_vals:
                            reference.timesCited = cite_vals[count]
                        device.backward_ref.append(reference)
                    except Exception as e:
                        print(e)
                        print("problem writing publisher")

            except Exception as e:
                print(e)

        count += 1


def writePublishers(title, biblStruct, ref_object):

    pubRef = biblStruct.find("{http://www.tei-c.org/ns/1.0}monogr")
    pubTitle = pubRef.find("{http://www.tei-c.org/ns/1.0}title").text

    if pubTitle is not title:
        publisher_title = pubTitle
    else:
        publisher_title = title

    imprint = pubRef.find("{http://www.tei-c.org/ns/1.0}imprint")

    publisher = imprint.find("{http://www.tei-c.org/ns/1.0}publisher")
    if publisher is not None:
        publisher_name = publisher.text
        publisher = publisher_title + ", " + publisher_name

    ref_object.publisher.name = publisher

    dateElem = imprint.find("{http://www.tei-c.org/ns/1.0}date")
    if dateElem is not None:
        if dateElem.get('type') == "published":
            date = dateElem.get('when')
            ref_object.publisher.date = date

    for biblScope in imprint.findall("{http://www.tei-c.org/ns/1.0}biblScope"):

        try:
            unit = biblScope.get('unit')
            val = biblScope.text

            if unit == 'page':
                if biblScope.get('from') and biblScope.get('to') is not None:
                    pages = biblScope.get('from') + " to " + biblScope.get('to')
                    ref_object.publisher.page = pages
            elif unit == 'volume':
                ref_object.publisher.volume = val
            elif unit == 'issue':
                ref_object.publisher.issue = val
        except Exception as e:
            print(e)
            pass


def writeAuthors(ref, ref_object):

    for author in ref.iter("{http://www.tei-c.org/ns/1.0}author"):
        persName = author.find("{http://www.tei-c.org/ns/1.0}persName")

        try:
            forename = persName.find("{http://www.tei-c.org/ns/1.0}forename")  # doesn't account mid names
            surname = persName.find("{http://www.tei-c.org/ns/1.0}surname")

            if forename is not None and surname is not None:
                if len(forename.text) == 1:
                    name = forename.text + '. ' + surname.text
                else:
                    name = forename.text = surname.text

            else:
                if surname is not None:
                    name = surname.text

                else:
                    name = ''

            if name is not '':
                ref_object.authors.append(name)

        except:
            pass


