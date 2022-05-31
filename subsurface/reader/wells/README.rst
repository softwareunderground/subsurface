Well data
=========

! This documentation is WIP

Well data is the most variable data sets we can import. To be able to accomodate as many
formats and data structures as possible, we are creating a pipeline. The main components of the pipeline
are:
1. the parsing to pandas dataframes containing collars, survey and properties
2. Creation of a `welly` project
3. Exporting data to pandas dataframes ready to create a `subsurface.unstructured` object


First step
----------

Example of data frames parsed:

*collar*

| 0   |      1 |           2 |     4 |
|:----|-------:|------------:|------:|
| foo | 691342 | 4.16401e+06 | 508.4 |
| bar | 691342 | 4.16401e+06 | 343.6 |


*survey*

| SITE_ID   |    md |   azi |   inc |
|:----------|------:|------:|------:|
| foo       |   0   | 165   | -90   |
| foo       |  12   | 191.4 | -89.5 |
| foo       |  30   | 216   | -89.7 |
| foo       |  60   | 231.4 | -89   |

*lith*

- ['altitude', 'base', 'component lith']
- ['top', 'base', 'component lith'] 

! Top and base are on well length


| SITE_ID   |   top |   base | component lith   |
|:----------|------:|-------:|:-----------------|
| foo       |   0   |   15.3 | F                |
| foo       |  15.3 |   16.9 | Pzneg            |
| foo       |  16.9 |   21.1 | F                |
| foo       |  21.1 |   22.4 | Pzneg            |
| foo       |  22.4 |   29.9 | F                |

Notes:
- It needs to have a column called md
- If inc or azi columns are not present the borehole is assumed to be vertical

*assay*
| BHID   |   basis |   Potencia |   Cu (%) |   Zn (%) |   Pb (%) |   Ag (ppm) |   Au (g/t) |   As (ppm) |
|:-------|--------:|-----------:|---------:|---------:|---------:|-----------:|-----------:|-----------:|
| foo    |   285   |        2   |    0.006 |   0.018  |   0.006  |        0.5 |     nan    |         25 |
| foo    |   287   |        2   |    0.012 |   0.015  |   0.0025 |        0.5 |     nan    |         25 |
| foo    |   289   |        1.5 |    0.017 |   0.012  |   0.0025 |        0.5 |     nan    |         70 |
| foo    |   290.5 |   