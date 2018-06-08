from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import xml.etree.ElementTree as ET

Base = declarative_base()

# Device class to represent a single data extracted from a PDF
class Device:

    def __init__(self, filename):

        title, self.back_ref = initialize_backref(filename)
        title = make_consistent(title)
        self.title = title
        self.fore_ref = initialize_foreref(title)


class RefTable(Base):
    __tablename__ = 'Reference Table'
    device = Column("Paper Name", String, primary_key=True, unique=False)
    reference = Column("Reference Name", String, primary_key=True, unique=False)


def initialize_backref(filename):

    tree = ET.parse(filename)
    root = tree.getroot()
    back_refs = []

    paper_title = next(root.iter("{http://www.tei-c.org/ns/1.0}title")).text
    for biblStruct in root.iter("{http://www.tei-c.org/ns/1.0}biblStruct"):

        if len(biblStruct.attrib.keys()) != 0:  # used to separate paper title from reference titles

            ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}analytic")

            if ref is None:
                # title is an analytic element, if not, then its a monogr element
                ref = biblStruct.find("{http://www.tei-c.org/ns/1.0}monogr")

            try:
                title = ref.find("{http://www.tei-c.org/ns/1.0}title").text
                title = make_consistent(title)
                # print("New Title: " + title)
                back_refs.append(title)

            except:
                pass

    return paper_title, back_refs

def initialize_foreref(title):
    fore_ref = []
    for device, in session.query(RefTable.device).filter_by(reference=title):
        fore_ref.append(device)

    return fore_ref

def make_consistent(title):
    allowed_char = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    title = ''.join(filter(allowed_char.__contains__, title))
    title = title.lower()
    return title


test_engine = create_engine('sqlite:///test_database.db', echo=True)
Base.metadata.create_all(test_engine)
Base.metadata.bind = test_engine

test_session = sessionmaker(bind=test_engine)

session = test_session()

test_device = Device("Vishard10.xml")
for ref in test_device.back_ref:
    new_ref = RefTable(device=test_device.title, reference=ref, ref_type="Back-Ref")
    session.add(new_ref)

for fore_ref in test_device.fore_ref:
    new_ref = RefTable(device=test_device.title, reference=ref, ref_type="Fore-Ref")
    session.add(new_ref)

print(str(len(test_device.fore_ref)))

test_device = Device("phantom.xml")
for ref in test_device.back_ref:
    new_ref = RefTable(device=test_device.title, reference=ref, ref_type="Back-Ref")
    session.add(new_ref)

for fore_ref in test_device.fore_ref:
    new_ref = RefTable(device=test_device.title, reference=ref, ref_type="Fore-Ref")
    session.add(new_ref)

print(str(len(test_device.fore_ref)))

session.commit()

session.close()
