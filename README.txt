[File Structure]
================

README (this)
ud032
  |
  |- Lesson_1_Data_Extraction_Fundamentals
  |- Lesson_1_Problem_Set
  |- Lesson_2_Data_in_More_Complex_Formats
  |- Lesson_2_Problem_Set
  |- .....etc.
  |- Lesson_6_OSM

In each case the above contains the given data sets and my corresponding solutions to lesson exercises and problem sets.  Lesson_6_OSM additionally contains a 'project' directory which contains all of the submitted material relating to the final project, this is explained further explained below.

./ud032/Lesson_6_OSM/project
  |
  |- data
  |- docs
  |- output
  |- src
      |
      |- queries

[data]
------

Contains the .osm sample file (as per instructions). Of course for the real project it contains the full dataset and is also where I output the product of cleansing ready for Mongo load

[docs]
------

This directory contains the final project report document and a variety of supporting text documents that further elaborate aspects of the project, these are referenced from the project report.

Final Project Report:  report.pdf
References:            references.txt
Map Position:          mapposition.txt

[output]
--------

This directory typically contains example output to various queries executed during audit and cleansing, file name typically mirrors the name of a corresponding query file (see src)

[src]
-----

This directory contains the primary python files used to audit and cleanse the data

* distinctusers.py     - list of distinct contributing users
* tagcount.py          - reports count of each tag
* streedaudit.py       - performs an audit of 'street types' (+ the code to map types to a prefered form)
* tagmongovalidity.py  - performs a character level audit of tags against mongo load rules

* wikitagaudit.py       - performs an audit of observed tag keys and values against best practice forms defined on the osm wiki
* json_convert_first.py - conversion (to mongo form) code for the initial pass
* json_convery_final.py - conversion (to mongo form) code for the final pass

[queries]
---------

Contains further software used to execute queries/aggregations against mongo during audit and cleanse process

* query.py & aggregate.py  - helper software that enable submission of a json file containing a query or aggregation respectively
* various .json files      - files containing a query or aggregation
* distinct_keys_mr.js      - javascript map reduce job to illustrate what keys are present and how often



