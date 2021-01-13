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


class test_download(unittest.TestCase):

    def test_get_latest_atel_number_function(self):

        from atelParser import download
        atels = download(
            log=log,
            settings=settings
        )
        latestNumber = atels.get_latest_atel_number()

    def testget_list_of_atels_still_to_download_function(self):

        from atelParser import download
        atels = download(
            log=log,
            settings=settings
        )
        atelsToDownload = atels.get_list_of_atels_still_to_download()
        atels.maxsleep = 7
        atels.download_list_of_atels(atelsToDownload[:1])

    def test_download_function_exception(self):

        from atelParser import download
        try:
            this = download(
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
