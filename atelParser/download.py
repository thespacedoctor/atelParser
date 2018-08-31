#!/usr/local/bin/python
# encoding: utf-8
"""
*Download ATels as Raw HTML files*

:Author:
    David Young

:Date Created:
    August 29, 2018
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
import requests
import re
import random
from time import sleep
import codecs


class download():
    """
    *The worker class for the download module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a download object, use the following:

        .. code-block:: python 

            from atelParser import download
            atels = download(
                log=log,
                settings=settings
            )  
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'download' object")
        self.settings = settings

        return None

    def get_latest_atel_number(
            self):
        """*get latest atel number by parsing the RSS feed for the ATel site*

        **Return:**
            - ``number`` -- the number of the latest ATel

        **Usage:**

            .. code-block:: python 

                from atelParser import download
                atels = download(
                    log=log,
                    settings=settings
                )
                latestNumber = atels.get_latest_atel_number()
        """
        self.log.debug('starting the ``get_latest_atel_number`` method')

        # DOWNLOAD THE RSS FEED FOR ATELS
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            response = requests.get(
                url="http://www.astronomerstelegram.org/?rss",
                headers=headers,
            )
            content = response.content
            status_code = response.status_code
        except requests.exceptions.RequestException:
            print 'HTTP Request failed'
            sys.exit(0)

        # PARSE ALL ATEL LINKS REPORTED
        matchObjectList = re.finditer(
            r'astronomerstelegram.org\/\?read\=(\d+)', content)
        atelNumbers = []
        atelNumbers[:] = [match.group(1) for match in matchObjectList]

        # FIND HIGHEST ATEL NUMBER
        atelNumbers = sorted(atelNumbers)
        number = int(atelNumbers[-1])

        self.log.debug('completed the ``get_latest_atel_number`` method')
        return number

    def _get_list_of_atels_still_to_download(
            self):
        """*get list of atels still to download by determining which ATels have been downloaded and diffing this against the latest ATel number*

        **Return:**
            - ``atelNumbersToDownload`` -- a list of the ATel numbers that need downloaded

        **Usage:**

            .. code-block:: python 

                from atelParser import download
                atels = download(
                    log=log,
                    settings=settings
                )
                atelsToDownload = atels._get_list_of_atels_still_to_download() 
        """
        self.log.debug(
            'starting the ``_get_list_of_atels_still_to_download`` method')

        basePath = self.settings["atel-directory"]

        atelDownloaded = []
        atelDownloaded[:] = [int(d.replace(".html", "")) for d in os.listdir(basePath) if os.path.isfile(
            os.path.join(basePath, d)) and ".html" in d]

        latestNumber = self.get_latest_atel_number()

        allAtels = range(1, latestNumber + 1, 1)
        atelNumbersToDownload = []
        atelNumbersToDownload[:] = [
            m for m in allAtels if m not in atelDownloaded]

        self.log.debug(
            'completed the ``_get_list_of_atels_still_to_download`` method')
        return atelNumbersToDownload

    def download_list_of_atels(
            self,
            atelNumbers):
        """*download the HTML files of all the missing ATels*

        **Key Arguments:**
            - ``atelNumbers`` -- the list of ATel numbers to download

        **Return:**
            - None

        **Usage:**

            To download new and missing ATel to your ``atel-directory`` use this code:

            .. code-block:: python 

                from atelParser import download
                atels = download(
                    log=log,
                    settings=settings
                )
                atelsToDownload = atels._get_list_of_atels_still_to_download()
                atels.download_list_of_atels(atelsToDownload)
        """
        self.log.debug('starting the ``download_list_of_atels`` method')

        for atel in atelNumbers:
            wait = random.randint(1, 180)
            print "Waiting for a randomly selected %(wait)ss before downloading ATel #%(atel)s" % locals()
            sleep(wait)
            url = 'http://www.astronomerstelegram.org/?read=%(atel)s' % locals(
            )
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            response = requests.get(url, headers=headers)
            pathToWriteFile = self.settings[
                "atel-directory"] + "/%(atel)0.8d.html" % locals()
            try:
                self.log.debug("attempting to open the file %s" %
                               (pathToWriteFile,))
                writeFile = codecs.open(
                    pathToWriteFile, encoding='utf-8', mode='w')
            except IOError, e:
                message = 'could not open the file %s' % (pathToWriteFile,)
                self.log.critical(message)
                raise IOError(message)
            writeFile.write(response.content.decode("utf8"))
            writeFile.close()

        self.log.debug('completed the ``download_list_of_atels`` method')
        return None
