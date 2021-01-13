# Latest ATel Count

The simplest tool in the `ATelParser` toolbox is the latest ATel count, reporting the number of the last reported ATel.

## From the Command-Line

To run the count from the command-line run:

```bash
> atel count
14318 ATels have been reported as of 2021/01/13 10:48:11s
```

## From Python Code

To get the count from python use the [`get_latest_atel_number`](./_api/atelParser.download.html#get_latest_atel_number) method:

```python
from atelParser import download
atels = download(
    log=log,
    settings=settings
)
latestNumber = atels.get_latest_atel_number()
```

