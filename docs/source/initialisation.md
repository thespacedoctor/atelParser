# Initialisation 

Before using atelParser you need to use the `init` command to generate a user settings file. Running the following creates a [yaml](https://learnxinyminutes.com/docs/yaml/) settings file in your home folder under `~/.config/atelParser/atelParser.yaml`:

```bash
atelParser init
```

The file is initially populated with atelParser's default settings which can be adjusted to your preference.

If at any point the user settings file becomes corrupted or you just want to start afresh, simply trash the `atelParser.yaml` file and rerun `atelParser init`.

## Modifying the Settings

Once created, open the settings file in any text editor and make any modifications needed. The most important setting is the `atel-directory` as this lets `atelParser` know where to download the ATel HTML files to. Change this value to your preferred location.

```yaml
atel-directory: ~/git_repos/atel-archive/html
```

## Basic Python Setup

If you plan to use `atelParser` in your own scripts you will first need to parse your settings file and set up logging etc. One quick way to do this is to use the `fundamentals` package to give you a logger, a settings dictionary and a database connection (if connection details given in settings file):

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

