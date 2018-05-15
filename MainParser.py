import os
import glob
import xml.etree.ElementTree as ET
import SectionParser
import ReferenceParser

forbidden_chars_table = str.maketrans('\/*?:"<>|', '_________')

def main():


    os.chdir("outputs")

    for file in glob.glob("*.xml"):

        tree = ET.parse(file)
        root = tree.getroot()

        paper_title = next(root.iter("{http://www.tei-c.org/ns/1.0}title")).text
        print("pre-translation: " + paper_title)
        paper_title = paper_title.translate(forbidden_chars_table)
        print("post-translation: " + paper_title)

        if len(paper_title) > 150:
            paper_title = paper_title[:150]
            paper_title = paper_title + "_"

        utf8_paper_title = paper_title.encode('ascii', 'ignore')

        if not os.path.exists(utf8_paper_title):
            os.makedirs(utf8_paper_title)

        os.chdir(utf8_paper_title)

        ReferenceParser.parseReference(root)
        SectionParser.parseSection(root)

        os.chdir('..')

if __name__ == '__main__':
    main()








