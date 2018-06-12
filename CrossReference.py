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
    ref_type = Column(String, unique=False)


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
    update_foreref(None, modified_name, session, "Initialize")  # check if this new paper has been cited before
    session.commit()

    return new_device, modified_name


# all names must be modified before putting into the database

def add_new_ref(device_name, title, session):

    title = modify_name(title)
    new_ref = RefTable(device=device_name, reference=title, ref_type='BackRef')
    session.add(new_ref)
    try:
        session.commit()
        print("--------------Backward-Ref Added: " + device_name + " Referred to " + title + "----------")
        update_foreref(device_name, title, session, "Update")
    except exc.IntegrityError:
        print("Skipping Duplicate")
        session.rollback()
        pass


def update_foreref(device_name, name, session, setting):
    #TODO: fix this duplicate code
    if setting is "Initialize":
        for device in session.query(RefTable.device).filter_by(reference=name, ref_type='BackRef'):
            new_ref = RefTable(device=name, reference=device, ref_type='ForeRef')
            session.add(new_ref)
            try:
                session.commit()
                print("--------------Forward-Ref Added: " + name + " Referred to: " + device + "----------")
            except:
                session.rollback()

    elif setting is "Update":
        for device in session.query(PaperTable.original_name).filter_by(modified_name=name):
            new_ref = RefTable(device=name, reference=device_name, ref_type='ForeRef')
            session.add(new_ref)
            try:
                session.commit()
                print("--------------Forward-Ref Added: " + device_name + " Referred to: " +  name + "----------")
            except:
                session.rollback()




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
