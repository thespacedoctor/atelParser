from __future__ import print_function
from builtins import str
import os
import unittest
import shutil
import yaml
from atelParser.utKit import utKit
from fundamentals import tools
from os.path import expanduser
home = expanduser("~")

packageDirectory = utKit("").get_project_root()
settingsFile = packageDirectory + "/test_settings.yaml"

su = tools(
    arguments={"settingsFile": settingsFile},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName=None,
    defaultSettingsFile=False
)
arguments, settings, log, dbConn = su.setup()

# SETUP PATHS TO COMMON DIRECTORIES FOR TEST DATA
moduleDirectory = os.path.dirname(__file__)
pathToInputDir = moduleDirectory + "/input/"
pathToOutputDir = moduleDirectory + "/output/"

try:
    shutil.rmtree(pathToOutputDir)
except:
    pass
# COPY INPUT TO OUTPUT DIR
shutil.copytree(pathToInputDir, pathToOutputDir)

# Recursively create missing directories
if not os.path.exists(pathToOutputDir):
    os.makedirs(pathToOutputDir)

settings["atel-directory"] = pathToOutputDir + "atel-directory"

def drop_database_tables(
        dbConn,
        log):
    log.debug('starting the ``drop_database_tables`` function')

    from fundamentals.mysql import writequery
    sqlQuery = """
        drop table if exists atel_coordinates;
        drop table if exists atel_names;
        drop table if exists atel_fullcontent;
        """ % locals()
    writequery(
        log=log,
        sqlQuery=sqlQuery,
        dbConn=dbConn
    )

    log.debug('completed the ``drop_database_tables`` function')
    return None
drop_database_tables(dbConn, log)

class test_mysql(unittest.TestCase):

    def test_01_atels_to_database_function(self):

        from atelParser import mysql
        parser = mysql(
            log=log,
            settings=settings
        )
        parser.atels_to_database()

    def test_02_parse_atels_function(self):

        from atelParser import mysql
        parser = mysql(
            log=log,
            settings=settings
        )
        parser.parse_atels()

    def test_03_update_htm_function(self):

        from atelParser import mysql
        parser = mysql(
            log=log,
            settings=settings
        )
        parser.populate_htm_columns()

    def test_04_mysql_function_exception(self):

        from atelParser import mysql
        try:
            this = mysql(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.get()
            assert False
        except Exception as e:
            assert True
            print(str(e))

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
