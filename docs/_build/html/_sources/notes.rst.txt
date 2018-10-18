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

To Keep In Mind
---------------

1. If running the program on 200+ PDF's, make sure to increase Java Heap Size to a larger value or this might cause PDFFigures2 to throw an OutOfMemoryError


Future Scripts
------------------

* UpdateTable.py

In case the title is incorrectly extracted, run ``UpdateTable.py old_name new_name``. This will find any extra connections
and will update the database given.
