=================
Other Information
=================

Connections
-----------
For every publication, there are three kinds of connections between publications

* Cross-Reference:

  * When one publication cites another publication and the number of times it was cited in the text

* Shared Authors:

  * When two publications share at least one author with each other

* Shared References:

    * When two publications shared at least one reference with each other

Database
--------
When database setting is set to true, extracted information will be added into a database. This setting only works if the tables and columns have the right names.

* Publication Table:

==============  ======= ===========
Column Name     Type    Description
==============  ======= ===========
id              serial  primary_key for publication
title           varchar title of the publication
authors         text[]  list of author ids from author table
all_references  JSON    references in JSON format - see references for more info
abstract        text    abstract of the publication
pub_date        varchar date of when the publication was published
publisher       varchar publisher of the publication
sections        varchar path to directory containing section text
figures         varchar path to directory containing figures and figure captions
backward_refs   JSON    **target**: publication referenced by current publication, **times_cited**: number of times cited in text
forward_refs    JSON    **target**: publication that cited current publication, **times_cited**: number of times cited in text
shared_authors  JSON    **target**: publication with shared authors, **shared_authors**: list of shared author ids
shared_refs     JSON    **target**: publication with shares references, **shared_refs**: list of shared references in JSON format
==============  ======= ===========


* Author Table:

============ ======= ===========
Column Name  Type    Description
============ ======= ===========
id           serial  primary_key for authors
author_name  varchar name of the author
publications text[]  list of publication id's of this author
============ ======= ===========

To Keep In Mind
---------------

1. If running the program on 200+ PDF's, make sure to increase Java Heap Size to a larger value or this might cause PDFFigures2 to throw an OutOfMemoryError


Additional Scripts
------------------

* UpdateTable.py

In case the title is incorrectly extracted, run ``UpdateTable.py old_name new_name``. This will find any extra connections
and will update the database given.
