# Parsing ATels To A Database

After downloading the ATel HTML files you now have the option of adding the content of the ATels to a MySQL database and to parse this content to generate indexed tables of coordinates and transient source names.

Connection details are needed in the ATel settings file for the parser to access the database.

The parser will create and populate the following 3 tables.

- `atel_fullcontent`: containing a list of ATels and their full-text content.
- `atel_names`: a list of transient source names found via regex matching of the ATel text content. Transients from new surveys and mangled names my get missed (please report via github issues if you find a problem).
- `atel_coordinates`: sky-position coordinates as parsed from the ATel content and converted to decimal degrees (also indexed via 3 different HTM level IDs). Some coordinates may have been missed if written in an obscure syntax (or just incorrectly).

The indexed transient source data in these tables can then be used in your own projects.

## From the Command-Line

To parse the downloaded ATels from the command-line run:

```bash
> atel parse
```

## From Python Code

If scripting the parsing of the ATels in your own code, use the [`mysql`](./_api/atelParser.mysql.html) class to parse the ATels and ingest them into the MySQL database tables:

```python
from atelParser import mysql
parser = mysql(
    log=log,
    settings=settings,
    reParse=reparseFlag
)
parser.atels_to_database()
parser.parse_atels()
parser.populate_htm_columns()
```



