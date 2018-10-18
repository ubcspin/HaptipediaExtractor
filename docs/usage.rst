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
  * Set-up database info in DatabaseInfo.py

Write To File Tool
~~~~~~~~~~~~~~~~~~
Setting to write all extracted data into the same directories that contain figures and figure captions for a publication


Before Running the program
---------------------------
1. Make sure GROBID is running in the background somewhere
2. Path to PDFFigures2 is written in ConfigPaths.py
3. Change AllowOCR = True in PDFFigures2
4. Put All PDF's to process in the directory HaptipediaExtractor/inputs
5. Have all desired settings set to True or False in ConfigPaths.py
6. Set Database Info in DatabaseInfo.py

Running the program
--------------------
1. To set-up the database, run in HaptipediaExtractor/src ``DBConfiguration.py``
  * Make sure to have set the database info inside DatabaseInfo.py
2. In the HaptipediaExtractor/src directory, run ``main.py``
