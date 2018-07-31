# HaptipediaAPI
An API for extracting metadata, text, section titles, figures, and references from Haptic Device Research Papers.
Uses PDFFigures2.0 for extraction of figures and figure captions and GROBID for extraction of references, section text and titles.
Also has a cross-reference function to find connections between given paper inputs (which papers cited each other and how many times, shared authors or references between papers).

Usage:
1. Set appropriate settings and directories for input and output files in ConfigPaths.py
2. Run MainExtractor.py

Dependencies:

Prereqs:
1. Python 3.5
2. subprocess32 package (pip install subprocess)

Python Libraries:
1. Psycopg2 (for connecting to the database)
2. Requests Library
3. 

Installation:
1. Clone the repo on the machine
2. Have GROBID running in the background somewhere

