from sqlalchemy import Column, String, create_engine, ForeignKey, exc
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

# Device class to represent a single data extracted from a PDF
class Device:

    def __init__(self, title):
        self.title = title
        self.backref = []
        self.foreref = []


# ref table for the papers a paper has referenced
class RefTable(Base):
    # all names are modified title of themselves
    __tablename__ = 'ReferenceTable'
    device = Column("Paper Name", String, primary_key=True, unique=False) # add foreign key later
    reference = Column("Reference Name", String, primary_key=True, unique=False)


class PaperTable(Base):
    __tablename__ = 'PaperTable'
    modified_name = Column(String, primary_key=True, unique=True)
    original_name = Column("Original Name", String)


# author table to access who wrote the paper, will have two attributes (one for paper name, one for the author
# both will be the primary keys for the table
# TODO: implement this after checking when PaperTable works
# class AuthorTable(Base):


def init_Device(paper_name, session):
    # this assumes that a session has already been created
    new_device = Device(paper_name)
    modified_name = modify_name(paper_name)
    new_paper = PaperTable(modified_name = modified_name, original_name = paper_name)
    session.add(new_paper)
    session.commit()

    return new_device, modified_name


def add_new_Ref(device_name, title, session):

    title = modify_name(title)
    new_ref = RefTable(device=device_name, reference=title)
    session.add(new_ref)
    try:
        session.commit()
    except exc.IntegrityError:
        print("Skipping Duplicate")
        session.rollback()
        pass

# def initialize_foreref(title):
#     fore_ref = []
#     for device, in session.query(RefTable.device).filter_by(reference=title):
#         fore_ref.append(device)
#
#     return fore_ref

def modify_name(title):
    if type(title) is not str:
        title = title.decode("ascii")
    allowed_char = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    title = ''.join(filter(allowed_char.__contains__, title))
    title = title.lower()
    return title


def create_session():
    engine = create_engine("sqlite:///test_database.db", echo=True)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    test_session = sessionmaker(bind=engine)

    return test_session()
