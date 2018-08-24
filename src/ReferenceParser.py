from CrossReference import modify_name
import re

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
        self.publisher = init_publisher_dict()
        self.timesCited = 1
        self.locations_cited = []


def init_ref_dict(title, ref_number):
    reference = {'title': title, 'ref_number': ref_number}
    reference['authors'] = []
    reference['publisher'] = init_publisher_dict()
    reference['times_cited'] = 1
    reference['locations_cited'] = []

    return reference

"""
Reference Parser that takes citation information from SectionParser to include in ref objects

"""


def parseReference(XMLroot, device, cite_vals, citation_placements, unaccounted_citations):

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
                    reference = init_ref_dict(title, count)

                    try:
                        writeAuthors(ref, reference)
                    except:
                        print("problem writing authors")
                    try:
                        writePublishers(title, biblStruct, reference)
                        if count in cite_vals:
                            reference['times_cited'] = cite_vals[count]
                            reference['locations_cited'] = citation_placements[count]
                        device.refs.append(reference)
                        device.ref_titles.append(reference['title'])
                    except Exception as e:
                        print(e)
                        print("problem writing publisher")

                    # update the unaccounted citations with all accounted citations removed
                    unaccounted_citations = update_unaccounted_citations(unaccounted_citations, reference)

            except Exception as e:
                print(e)

        count += 1


"""
For each unaccounted_citation, check if they are connected to this reference. If it's not connected to this
ref, then add it to a new list. The new list will be all the remaining unaccounted_citations, this will get passed to
the next reference to be checked.
"""


def update_unaccounted_citations(unaccounted_citations, reference):
    remaining_unaccounted_citations = []
    for citation in unaccounted_citations:
        if check_reference(citation[0], reference):
            reference['times_cited'] += 1
            if citation[1] not in reference['locations_cited']:
                reference['locations_cited'].append(citation[1])
        else:
            # if citation is not connected to this reference, add it into the new list
            remaining_unaccounted_citations.append(citation)

    return remaining_unaccounted_citations


"""
Compares the reference year and the year on the citation, if they are the same, check their authors
"""


def check_reference(citation, reference):
    ref_year = re.findall(r'\d\d\d\d', reference['publisher']['date'])
    cite_year = re.findall(r'\d\d\d\d', citation)

    if cite_year != '' and ref_year != '' and cite_year == ref_year:
        return check_authors(citation, reference['authors'])
    else:
        return False


def check_authors(citation, authors):
    author_names = extract_author_names(citation)

    for name in author_names:
        for author in authors:
            author_split = author.split(' ')
            author = author_split[len(author_split) - 1]
            if name == author:
                return True
    return False


def extract_author_names(citation_str):
    delete_table = str.maketrans('1234567890().,', '______________')
    author_name = citation_str.translate(delete_table)
    author_name = author_name.replace('_', '')
    names = author_name.split(' ')

    author_names = []
    for name in names:
        if len(name) > 1:
            if name not in ['et', 'al', 'and']:
                author_names.append(name)

    return author_names


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
        ref_object['publisher']['name'] = publisher

    dateElem = imprint.find("{http://www.tei-c.org/ns/1.0}date")
    if dateElem is not None:
        if dateElem.get('type') == "published":
            date = dateElem.get('when')
            ref_object['publisher']['date'] = date

    for biblScope in imprint.findall("{http://www.tei-c.org/ns/1.0}biblScope"):

        try:
            unit = biblScope.get('unit')
            val = biblScope.text

            if unit == 'page':
                if biblScope.get('from') and biblScope.get('to') is not None:
                    pages = biblScope.get('from') + " to " + biblScope.get('to')
                    ref_object['publisher']['pages'] = pages
            elif unit == 'volume':
                ref_object['publisher']['volume'] = val
            elif unit == 'issue':
                ref_object['publisher']['issue'] = val
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
                ref_object['authors'].append(name)

        except:
            pass


def init_publisher_dict():
    publisher = {'name': '', 'date': '', 'pages': '', 'volume': '', 'issue': ''}

    return publisher


