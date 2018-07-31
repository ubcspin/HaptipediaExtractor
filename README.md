# HaptipediaAPI
An API for extracting metadata, text, section titles, figures, and references from Haptic Device Research Papers.
Uses PDFFigures2.0 for extraction of figures and figure captions and GROBID for extraction of references, section text and titles.
Also has a cross-reference function to find connections between given paper inputs (which papers cited each other and how many times, shared authors or references between papers).

# Usage 
1. Set appropriate settings and directories for input and output files in ConfigPaths.py
2. Run MainExtractor.py

# Dependencies 

## Prereqs
1. Python 3.5
2. subprocess32 package (pip install subprocess)

## Python Libraries
1. Psycopg2 (for connecting to the database)
2. Requests Library

## Installation
1. Clone the repo on the machine
2. Have GROBID running in the background somewhere

# GROBID
Grobid is used to extract metadata, text and citations from PDF files. Grobid should be running as a service somwhere. (Run mvn jetty:run-war from grobid-service directory if not already running. See Grobid's Github project for more complete installation instructions.)

# PDFFigures2.0
Pdffigures2.0 is used to extract figures, tables and captions from PDF files. It should be installed as directed by the pdffigures2 Github page. The path to the pdffigures2 binary can be configured in ConfigPaths.py

