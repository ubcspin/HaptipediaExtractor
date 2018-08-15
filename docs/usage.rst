=====
Usage
=====

Different Settings:
-------------------

Cross-Reference Tool
~~~~~~~~~~~~~~~~~~~~
* Setting to find cross-references and connections between input publications
  * If database tool is also turned on, the program will find connections the input publications has with publications already in the database
  * See Connections Page to see what connections are defined

Add To Database Tool
~~~~~~~~~~~~~~~~~~~~
* Setting to add extracted data into the database
  * Database schema must have tables and columns that are defined in Tables Page

Write To File Tool
~~~~~~~~~~~~~~~~~~
Setting to write all extracted data into the same directories that contain figures and figure captions for a publication


Before Running the program
---------------------------
1. Make sure GROBID is running in the background somewhere
2. Path to PDFFigures2 is written in ConfigPaths.py
3. Change AllowOCR = True in PDFFigures2
4. Input and Output Directories is written in ConfigPaths.py
5. Have all desired settings set to True or False in ConfigPaths.py

Running the program
--------------------

In the HaptipediaExtractor directory, type in the command line
``run main.py``
