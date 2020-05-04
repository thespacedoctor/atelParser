#!/usr/local/bin/python
# encoding: utf-8
"""
Documentation for atelParser can be found here: http://atelParser.readthedocs.org/en/stable

Usage:
    atel init
    atel count [-s <pathToSettingsFile>]
    atel download [-s <pathToSettingsFile>]
    atel [-r] parse [-s <pathToSettingsFile>]

Options:
    init                  setup the atelParser settings file for the first time
    count                 report the total number of atels reported so far
    download              download new and remaining ATel to the atel-directory stated in settings file
    parse                 add the new ATel contents to database and parse for names and coordinates


    -h, --help            show this help message
    -v, --version         show version
    -s, --settings        the settings file
    -r, --reparse         re-parse all ATel for names and coordinates
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import pickle
from docopt import docopt
from fundamentals import tools, times
from subprocess import Popen, PIPE, STDOUT
# from ..__init__ import *


def tab_complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


def main(arguments=None):
    """
    *The main function used when ``cl_utils.py`` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="WARNING",
        options_first=False,
        projectName="atelParser",
        defaultSettingsFile=True
    )
    arguments, settings, log, dbConn = su.setup()

    # tab completion for raw_input
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tab_complete)

    # unpack remaining cl arguments using `exec` to setup the variable names
    # automatically
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if varname == "import":
            varname = "iimport"
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    # set options interactively if user requests
    if "interactiveFlag" in locals() and interactiveFlag:

        # load previous settings
        moduleDirectory = os.path.dirname(__file__) + "/resources"
        pathToPickleFile = "%(moduleDirectory)s/previousSettings.p" % locals()
        try:
            with open(pathToPickleFile):
                pass
            previousSettingsExist = True
        except:
            previousSettingsExist = False
        previousSettings = {}
        if previousSettingsExist:
            previousSettings = pickle.load(open(pathToPickleFile, "rb"))

        # x-raw-input
        # x-boolean-raw-input
        # x-raw-input-with-default-value-from-previous-settings

        # save the most recently used requests
        pickleMeObjects = []
        pickleMe = {}
        theseLocals = locals()
        for k in pickleMeObjects:
            pickleMe[k] = theseLocals[k]
        pickle.dump(pickleMe, open(pathToPickleFile, "wb"))

    if init:
        from os.path import expanduser
        home = expanduser("~")
        filepath = home + "/.config/atelParser/atelParser.yaml"
        try:
            cmd = """open %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass
        try:
            cmd = """start %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass
        return

    if download:
        from atelParser import download
        atels = download(
            log=log,
            settings=settings
        )
        atelsToDownload = atels._get_list_of_atels_still_to_download()
        atels.download_list_of_atels(atelsToDownload)

    if count:
        from atelParser import download
        atels = download(
            log=log,
            settings=settings
        )
        latestNumber = atels.get_latest_atel_number()
        from datetime import datetime, date, time
        now = datetime.now()
        now = now.strftime("%Y/%m/%d %H:%M:%Ss")
        print "%(latestNumber)s ATels have been reported as of %(now)s" % locals()

    if parse:
        from atelParser import mysql
        parser = mysql(
            log=log,
            settings=settings,
            reParse=reparseFlag
        )
        parser.atels_to_database()
        parser.parse_atels()
        parser.populate_htm_columns()

    # CALL FUNCTIONS/OBJECTS

    if "dbConn" in locals() and dbConn:
        dbConn.commit()
        dbConn.close()
    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE cl_utils.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return


if __name__ == '__main__':
    main()
