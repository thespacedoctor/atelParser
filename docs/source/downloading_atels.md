# Downloading ATels

## From the Command-Line

To download new/missing ATels run `atel download` from the command-line:

```bash
> atel download
Waiting for a randomly selected 35s before downloading ATel #14317
Waiting for a randomly selected 101s before downloading ATel #14318
...
```

Note a random time between 0-180s is injected between ATel page downloads so not to overwhelm the ATel servers.

## From Python Code

Before you begin to code you will need to parse your settings file and set up logging etc. One quick way to do this is to use the `fundamentals` package to give you a logger, a settings dictionary and a database connection (if connection details given in settings file):

```python
## SOME BASIC SETUP FOR LOGGING, SETTINGS ETC
from fundamentals import tools
from os.path import expanduser
home = expanduser("~")
settingsFile  = home + "/.config/atelParser/atelParser.yaml"
su = tools(
    arguments={"settingsFile": settingsFile},
    docString=__doc__,
)
arguments, settings, log, dbConn = su.setup()
```

Assuming you have set up your `atel-directory` location in the settings file (see [Initialisation](./initialisation.md)), you can download all new/missing ATels pages with the following code snippet.

```python
## DOWNLOAD ALL NEW ATEL PAGES
from atelParser import download
atels = download(
    log=log,
    settings=settings
)
atelsToDownload = atels.get_list_of_atels_still_to_download()
atels.download_list_of_atels(atelsToDownload)
```

Once run, you should find one HTML file per ATel in your `atel-directory` folder. You can find more information on the [`download` class here](./_api/atelParser.download.html)
