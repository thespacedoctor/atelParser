#!/usr/local/bin/python
# encoding: utf-8
"""
*Import ATel into MySQL database and parse for names and coordinates*

:Author:
    David Young

:Date Created:
    August 30, 2018
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools, times
import re
import sys
from datetime import datetime
from fundamentals.mysql import database, readquery, writequery, convert_dictionary_to_mysql_table
import codecs
from astrocalc.coords import unit_conversion


class mysql():
    """
    *The worker class for the mysql module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``reParse`` -- re-parse all existing atels? Useful if new names have been added to the parse-list

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a mysql object, use the following:

        .. code-block:: python 

            from atelParser import mysql
            parser = mysql(
                log=log,
                settings=settings
            ) 
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,
            reParse=False

    ):
        self.log = log
        log.debug("instansiating a new 'mysql' object")
        self.settings = settings
        self.reParse = reParse

        # SETUP ALL DATABASE CONNECTION
        self.dbSettings = settings["database settings"]
        self.dbConn = database(
            log=log,
            dbSettings=self.dbSettings
        ).connect()

        return None

    def atels_to_database(
            self):
        """*Parse ATels into a mysql db. Parser to add ATels into a mysql db - each ATel has 'element' data (top level - title, author ...) and 'item' data (object specific data - ra, dec, mag, name ...).
            The parser will add one row per 'item' (object) into the db table*

        **Return:**
            - None

        **Usage:**

            .. code-block:: python 

                from atelParser import mysql
                parser = mysql(
                    log=log,
                    settings=settings
                )
                parser.atels_to_database()
        """
        self.log.debug('starting the ``atels_to_database`` method')

        # LIST ALL PARSED ATEL NUMBERS IN DATABASE
        sqlQuery = u"""
            SELECT distinct atelNumber
                        FROM atel_fullcontent
                        ORDER BY atelNumber DESC
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn,
            quiet=False
        )
        databaseAtels = []
        databaseAtels = []
        databaseAtels[:] = [int(l['atelNumber']) for l in rows]

        # LIST HTML ATEL FILES DOWNLOADED
        basePath = self.settings["atel-directory"]
        atelDownloaded = []
        atelDownloaded[:] = [int(d.replace(".html", "")) for d in os.listdir(basePath) if os.path.isfile(
            os.path.join(basePath, d)) and ".html" in d]

        # CREATE LIST OF FILES TO NOW PARSE
        atelsToParse = []
        atelsToParse[:] = [self.settings["atel-directory"] +
                           "/%(a)0.8d.html" % locals() for a in atelDownloaded if a not in databaseAtels]

        # LOOP THROUGH THE ATEL FILES AND ADD THE VARIOUS HTML ELEMENTS AND TAGS TO
        # DB
        for atel in atelsToParse:
            if not atel:
                continue

            # READ HTML FILE
            try:
                self.log.debug("attempting to open the file %s" % (atel,))
                readFile = codecs.open(atel, encoding='utf-8', mode='r')
                html = readFile.read()
                readFile.close()
            except IOError, e:
                message = 'could not open the file %s' % (atel,)
                self.log.critical(message)
                raise IOError(message)

            elementDict = {}

            # ATEL TITLE
            reTitle = re.compile(
                r'<TITLE>.*?#\d{1,5}:\s?(.*?)\s?<\/TITLE>', re.M | re.I)
            try:
                title = reTitle.search(html).group(1)
            except:
                # QUIT WHENEVER A TITLE IS NOT FOUND IN THE HTML DOC (i.e. ATEL
                # DOES NOT EXIST YET)
                return
                title = None
            elementDict['title'] = title

            # ATEL NUMBER
            reAtelNumber = re.compile(
                r'<P ALIGN=CENTER>\s?ATel\s?#(\d{1,5})', re.M | re.I)
            try:
                atelNumber = reAtelNumber.search(html).group(1)
            except:
                atelNumber = None
            # print atelNumber
            elementDict['atelNumber'] = atelNumber

            # ATEL AUTHORS
            reWho = re.compile(
                r'<A HREF=\"mailto:([\w.\-@]*)\">(.*?)<', re.M | re.I)
            try:
                email = reWho.search(html).group(1)
                authors = reWho.search(html).group(2)
            except:
                email = None
                authors = None
            elementDict['email'] = email
            elementDict['authors'] = authors

            # ATEL DATETIME
            redateTime = re.compile(
                r'<STRONG>(\d{1,2}\s\w{1,10}\s\d{4});\s(\d{1,2}:\d{2})\sUT</STRONG>', re.M | re.I)
            try:
                date = redateTime.search(html).group(1)
                time = redateTime.search(html).group(2)

            except:
                date = None
                time = None

            datePublished = date + " " + time
            datePublished = datetime.strptime(datePublished, '%d %b %Y %H:%M')
            # print "datePublished = %s" % (datePublished,)
            elementDict['datePublished'] = datePublished

            # ATEL
            reTags = re.compile(
                r'<p class="subjects">Subjects: (.*?)</p>', re.M | re.I)
            try:
                tags = reTags.search(html).group(1)
            except:
                tags = None
            elementDict['tags'] = tags

            # ATEL USER ADDED TEXT
            reUserText = re.compile(
                r'</div id="subjects">.*?(<div id="references">.*?</div id="references">)?<P>(.*)</P>.*?(<a href="http://twitter.com/share|</TD><TD>)', re.S | re.I)
            try:
                userText = reUserText.search(html).group(2)
            except:
                userText = None
            elementDict['userText'] = userText

            # FIND REFS IN USER ADDED TEXT
            refList = []
            reOneRef = re.compile(
                r'http:\/\/www.astronomerstelegram.org\/\?read=(\d{1,5})', re.M | re.I)
            try:
                refIter = reOneRef.finditer(userText)
            except:
                refIter = None
            if refIter:
                for item in refIter:
                    refList.extend([item.group(1)])
            else:
                pass
            refList = set(refList)
            refList = ", ".join(refList)
            elementDict['refList'] = refList

            # ATEL BACK REFERENCES - FIND EXTRA BACK REFS IN REFERENCE DIV
            reBacksRefs = re.compile(
                r'<div id="references">(.*?)</div id="references">', re.M | re.I)
            try:
                backRefs = reBacksRefs.search(html).group(1)
            except:
                backRefs = None
            backRefList = []
            reOneBackRef = re.compile(
                r'<A HREF="http:\/\/www.astronomerstelegram.org\/\?read=(\d{1,7})">\1</a>', re.M | re.I)
            try:
                backRefIter = reOneBackRef.finditer(backRefs)
            except:
                backRefIter = None
            if backRefIter:
                for item in backRefIter:
                    # print item.group(1)
                    backRefList.extend([item.group(1)])
            else:
                # print backRefIter
                pass
            # REMOVE DUPLICATE ATEL NUMBERS FROM LIST
            backRefList = set(backRefList)
            backRefList = ", ".join(backRefList)
            elementDict['backRefList'] = backRefList

            convert_dictionary_to_mysql_table(
                dbConn=self.dbConn,
                log=self.log,
                dictionary=elementDict,
                dbTableName="atel_fullcontent",
                uniqueKeyList=["atelNumber"],
                dateModified=False,
                returnInsertOnly=False,
                replace=False,
                batchInserts=False,  # will only return inserts,
                reDatetime=re.compile(
                    '^[0-9]{4}-[0-9]{2}-[0-9]{2}T')  # OR FALSE
            )

        self.log.debug('completed the ``atels_to_database`` method')
        return None

    def parse_atels(
            self):
        """*Parse the content of the ATels in the database, appending the various components and values to the db. Also includes the ability convert the atels to markdown, highlighting matches of the parsing regexs.*

        **Return:**
            - None

        **Usage:**

                - write a command-line tool for this method
                - update package tutorial with command-line tool info if needed

            .. code-block:: python 

                from atelParser import mysql
                parser = mysql(
                    log=log,
                    settings=settings
                )
                parser.parse_atels()
        """
        self.log.debug('starting the ``parse_atels`` method')

        ################ > VARIABLE SETTINGS ######
        # METRICS TO FILTER ATELS
        numReferences = 0  # NUMBER OF REFERENCES WITH ATEL
        tags = ""  # ATEL TAGS
        numCoords = 0  # NUMBER OF COORDINATE PAIRS IN ATEL
        numHeaderName = 0  # NUMBER OF NAMES IN HEADER
        numTextName = 0  # NUMBER OF NAMES IN TEXT
        discHead = 0  # DISCOVERY KEYWORD FOUND IN HEADER?
        obsHead = 0  # OBSERVATION KEYWORD FOUND IN HEADER?
        clasHead = 0  # CLASSIFICATION KEYWORD FOUND IN HEADER?
        correctionHead = 0  # CORRECTION KEYWORD FOUND IN HEADER?
        discText = 0  # DISCOVERY KEYWORD FOUND IN TEXT?
        obsText = 0  # OBSERVATION KEYWORD FOUND IN TEXT?
        clasText = 0  # CLASSIFICATION KEYWORD FOUND IN TEXT?
        comment = 0  # COMMENT TAG IN ATEL

        # ASTROCALC UNIT CONVERTER OBJECT
        converter = unit_conversion(
            log=self.log
        )

        # SELECT UNPROCESSED ATELS
        if self.reParse == False:
            whereClause = "dateParsed is NULL"
        else:
            whereClause = "1=1"
        sqlQuery = u"""SELECT *
                        FROM atel_fullcontent
                        where %(whereClause)s 
                        ORDER BY atelNumber""" % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn,
            quiet=False
        )

        # REGEX BUILDS
        start = r"""((R\.?A\.?\b|Coord)[/()\w\d\s,.]{0,9}(\(J2000(\.0)?\)\s?)?(=|:|\s)|\d{4}-\d{2}-\d{2})\s{0,2}[+(]{0,2}"""
        middle = r"""(\sdeg)?(\s?,|:)?\s{0,2}(and\s{1,2}|\(?[\ddeg.':\s]{1,16}\)?(;|,)?\s{0,3})?(Decl?\.?\s*?[()\w\d\s]{0,9}(=|:|\s))?\s?"""
        end = r"""(\sdeg)?"""
        raSex = r"""(?P<raSex>(
                                (?P<raHrs>\d|[0-1]\d|[2][0-3])(:\s?|\s|h\s?)
                                (?P<raMin>[0-5][0-9])(:\s?|\s|m\s?)
                                (?P<raSec>[0-5]\d|\d(?!\d))s?(?P<raSubSec>\.\d{1,})?(\s|\s?s)?
                            )
                    )"""
        decSex = r"""(?P<decSex>(
                                (?P<decDeg>(\+|-|–)?[0-8]\d)(:\s?|\s|d\s?|deg\s|o\s?)
                                (?P<decMin>[0-5][0-9])(:\s?|\s|m\s?|'?\s?)
                                (?P<decSec>[0-5]?\d)'?\s?(?P<decSubSec>\.\d{1,3})?'?s?
                            )
                    )"""
        raDeg = r"""
                    (?P<raDDeg>\d{1,3}(\.\d{1,}))
                """
        decDeg = r"""
                    (?P<decDDeg>[\+\-\–]?\d{1,3}(\.\d{1,}))
                """

        nameList = [
            r"""(PSN|PNV)\s?J\d{8}(\+|-|–)\d{3}(\+|-|–)?\d{3,4}""",
            r"""(SN|Supernova)\s?(19|20)\d{2}[A-Za-z]{1,4}""",
            r"""GX\s?\d{3}(\+|-|–)\d""",
            r"""Fermi\s?J\d{4}(\+|-|–)\d{4}""",
            r"""PHL\s?\d{3}""",
            r"""QSO\s?B\d{4}(\+|-|–)\d{3}""",
            r"""i?PTF(0|1)\d[a-zA-Z]{1,3}""",
            r"""MASTER\s?((short\s)?ot\s)?J?\d{6}\.\d{2}(\+|-|–)\d{6}\.\d""",
            r"""(FSRQ\s?)?PKS\s?\d{4}(\+|-|–)\d{3}""",
            r"""BZQ\s?J\d{4}(\+|-|–)\d{4}""",
            r"""(SN(-|–))?LSQ1\d[a-zA-Z]{1,4}""",
            r"""M31N\s?(19|20)\d{2}(\+|-|–)\d{2}[a-z]""",
            r"""IGR\s?J?\d{5}(\+|-|–)?\d{1,4}""",
            r"""GRS\s?\d{4}(\+|-|–)\d{1,4}""",
            r"""PS1(-|–)?(0|1)\d[a-zA-Z]{1,3}""",
            r"""PS1\d[a-zA-Z]{1,3}""",
            r"""SDSS\s(galaxy\s)?J\d{6}\.\d{2}(\+|-|–)\d{6}\.\d""",
            r"""(CSS|MLS|SSS)\d{6}:\d{6}(\+|-|–)\d{6}""",
            r"""XMM(U|SL1)\s?J\d{6}\.\d{1}(\+|-|–)\d{6}""",
            r"""SAX\s?J\d{4}\.\d(\+|-|–)\d{3,4}""",
            r"""1RXS\s?J\d{6}\.\d(\+|-|–)\d{6}""",
            r"""USNO(-|–)(B1|A2)\.0\s?(catalogue\s?)\d{4}(-|–)\d{7}""",
            r"""KS\s?\d{4}(\+|-|–)\d{3}""",
            r"""AX\s?J\d{4}\.\d(\+|-|–)\d{4}""",
            r"""2MAS(S|X)\s?J?\d{8}(\+|-|–)\d{7}""",
            r"""SWIFT\s?J\d{4,6}\.\d(\+|-|–)\d{1,6}""",
            r"""4U\s?\d{4}(\+|-|–)\d{2,4}""",
            r"""Hen\s\d{1}(\+|-|–)\d{4}""",
            r"""(HMXB\s?)?XTE\s?J?\d{4}(\+|-|–)\d{3}""",
            r"""MAXI\s?J?\d{4}(\+|-|–)\d{3}""",
            r"""PG\s?J?\d{4}(\+|-|–)\d{3}""",
            r"""PMN\s?J?\d{4}(\+|-|–)\d{4}""",
            r"""Guide\sStar\sCatalog\sN4HU\d{6}""",
            r"""CXOGBS\s?J?\d{6}\.8(\+|-|–)\d{6}""",
            r"""Galactic\sPlane\s(gamma-ray\s)?Transient\sJ?\d{4}(\+|-|–)\d{4}""",
            r"""TXS\s\d{4}(\+|-|–)\d{3}""",
            r"""V\d{4}\sSgr""",
            r"""Aql\sX(\+|-|–)1""",
            r"""BLAZAR\s[a-zA-Z\d]{2}\s?\d{3,4}((\+|-|–)\d{2})?""",
            r"""SNhunt\s\d{1,5}""",
            r"""Nova\s[a-zA-Z]{3}\s(19|20)\d{2}""",
            r"""GRB\s?\d{6}[a-zA-Z]{1,2}""",
            r"""\bV\d{3,4}\s(Sagittarii|cyg)""",
            r"""SGR\s\d4(\+|-|–)\d{2}""",
            r"""(QSO|3EG|2FGL)\s?J?\d{4}(\.\d)?(\+|-|–)\d{4}""",
            r"""BL\sLacertae""",
            r"""\bCTA\s\d{3}""",
            r"""ASASSN( |–|-)1\d[a-zA-Z]{1,4}""",
            r"""OGLE-201\d-(SN|NOVA)-\d{1,4}""",
            r"""OGLE ?1\d[a-zA-Z]{1,4}""",
            r"""Gaia ?1\d[a-zA-Z]{1,4}""",
            r"""DES1\d[a-zA-Z]\d[a-zA-Z]{1,4}""",
            r"""HFF1\d[a-zA-Z]{1,4}""",
            r"""HSC-SN1\d[a-zA-Z]{1,4}""",
            r"""MASTER ?J\d{5,6}\.\d{2}\+\d{5,6}\.\d{1,2}""",
            r"""SKY( |-|–|_)J\d{6,8}(-|–|\+)\d{6,8}""",
            r"""SMT ?\d{6,8}(-|–|\+)\d{6,8}""",
            r"""SN20\d{2}[a-zA-Z]{1,4}""",
            r"""TCP ?J\d{6,8}(-|–|\+)\d{6,8}""",
            r"""ATLAS\d{2}\w{1,8}""",
            r"""AT20\d{2}[a-zA-Z]{1,4}""",
            r"""ZTF\d{2}[a-zA-Z]{1,15}"""
        ]

        # JOIN ALL THE NAMES INTO ONE STRING
        nameStr = ("|").join(nameList)
        # REGEX TO SEARCH FOR OBJECT NAMES IN THE ATEL BODIES
        reName = re.compile(r"""(%s)""" % (nameStr,), re.S | re.I)

        # REGEX TO SEARCH FOR SEXEGESIMAL COORDINATES WITHIN THE BODY TEXT
        reSexeg = r"""
                        %s
                        %s
                        %s
                        %s
                        %s
                    """ % (start, raSex, middle, decSex, end)

        reSexeg = re.compile(r"""%s""" % (reSexeg), re.S | re.I | re.X)

        # REGEX TO SEARCH FOR DECIMAL DEGREES COORDINATES WITHIN THE BODY TEX
        reDegree = r"""
                        %s
                        %s
                        (\sdeg)?(\s?,|:)?\s{0,2}(and\s{1,2}|\(?%s\)?(;|,)?\s{0,3})?(Decl?\.?\s*?[()\w\d\s]{0,9}(=|:|\s))?\s?
                        %s
                        %s""" % (start, raDeg, raSex, decDeg, end,)

        reDegree = re.compile(r"""%s""" % (reDegree,), re.S | re.I | re.X)

        # REGEX TO SEARCH FOR SEXEG COORDINATES IN TABLES
        reSexTable = r"""
                        %s
                        \s?(\||</td>\s?<td>)?\s?
                        %s
                    """ % (raSex, decSex,)

        reSexTable = re.compile(r"""%s""" % (reSexTable, ), re.S | re.I | re.X)

        # REGEX TO FIND THE SUPERNOVA TYPE
        reSNType = re.compile(
            r'type\s(I[abcilps]{1,3}n?)|(\bI[abcilnps]{1,3}n?)\s(SN|supernova)|<td>\s?\b(I[abcilps]{1,3}n?)\b\s?<\/td>|(SN\simpostor)|\|\s?\b(I[abcilps]{1,3}n?)\b\s?\||(SN|supernova)\s?(I[abcilps]{1,3}n?)', re.S | re.I)

        # ITERATE THROUGH THE NEW UNPROCESSED ATELS
        for row in rows:
            atelNumber = row["atelNumber"]
            userText = row["userText"]

            self.log.info("""parsing atel: `%(atelNumber)s`""" % locals())
            # convert bytes to unicode
            if isinstance(userText, str):
                userText = unicode(
                    userText, encoding="utf-8", errors="replace")

            # SETUP HEADERS FOR MD -- USED FOR DEBUGGING
            header = "\n# %s: %s" % (row["atelNumber"], row["title"],)
            references = "\n### **REFS:** %s" % (row["refList"],)
            # numReferences = len(row["refList"])
            tags = "\n### **TAGS:** %s" % (row["tags"],)

            # REMOVE NIGGLY STRINGS TO MAKE PARSING EASIER
            stringsToRemove = [
                u"<p>",
                u"</p>",
                u"<P>",
                u"</P>",
                u"<P ALIGN=CENTER><EM><A HREF='http://'></A></EM>",
                u"<pre>",
                u"</pre>",
                u"#",
                u"<b>",
                u"</b>",
                u"<br>",
                u"</br>",
                u"<P ALIGN=CENTER>",
                u"<EM>",
                u"</EM>",
                u"<sup>",
                u"</center>",
                u"<center>",
                u"</sup>",
                u"<sub>",
                u"</sub>",
                u"<SUP>",
                u"</CENTER>",
                u"<CENTER>",
                u"</SUP>",
                u"<SUB>",
                u"</SUB>",
                u"<br />",
                u"<pre />",
                u"<pre/>",
                u"<PRE>",
                u"<Pre>",
                u"<it>",
                u"</it>",
                u"<A ",
                u"</a>",
                u"</A>",
                u"<a ",
                u"_",
                u"--",
                u"</BR>",
                u"<BR>",
                u"&deg;",
                u"</div>",
                u"<div>",
                u"Ã?Â",
                u" ",
                u"***",
                u"<B>",
                u"</B>",
                u"\n"
            ]
            for item in stringsToRemove:
                userText = userText.replace(item, "")

            for i in range(0, 6):
                userText = userText.replace("  ", " ")
            userText = userText.replace(";", ":")
            userText = userText.replace("&plusmn: 0.001", "")

            # SEARCH FOR SEXEGESIMAL COORDINATES WITHIN THE BODY TEXT
            try:
                sIter = reSexeg.finditer(userText)
            except:
                sIter = None

            # 14h 59m 36.51s -71d 46m 60.0s

            sList = []
            for item in sIter:
                # CONVERT RA DEC TO DECIMAL DEGREES
                raSec = item.group('raSec')
                if item.group('raSubSec'):
                    raSec += item.group('raSubSec')
                decSec = item.group('decSec')
                if item.group('decSubSec'):
                    decSec += item.group('decSubSec')
                _raSex = """%s:%s:%s""" % (
                    item.group('raHrs'), item.group('raMin'), raSec)
                _decSex = """%s:%s:%s""" % (
                    item.group('decDeg'), item.group('decMin'), decSec)

                raDegrees = converter.ra_sexegesimal_to_decimal(
                    ra=_raSex
                )
                decDegrees = converter.dec_sexegesimal_to_decimal(
                    dec=_decSex
                )

                sList.extend([[str(raDegrees), str(decDegrees)]])
                userText = userText.replace(
                    item.group('raSex'), " **<font color=blue>" + item.group('raSex') + " </font>** ")
                userText = userText.replace(
                    item.group('decSex'), " **<font color=blue>" + item.group('decSex') + " </font>** ")

            # SEARCH FOR DECIMAL DEGREES COORDINATES WITHIN THE BODY TEXT
            try:
                sIter2 = reDegree.finditer(userText)
            except:
                sIter2 = None

            for item in sIter2:
                # print item.group('raDDeg'), item.group('decDDeg')
                sList.extend([[item.group('raDDeg'), item.group('decDDeg')]])
                userText = userText.replace(
                    item.group('raDDeg'), " **<font color=green>" + item.group('raDDeg') + " </font>** ")
                userText = userText.replace(
                    item.group('decDDeg'), " **<font color=green>" + item.group('decDDeg') + " </font>** ")

            # SEARCH FOR SEXEG COORDINATES IN TABLES
            try:
                sIter3 = reSexTable.finditer(userText)
            except:
                sIter3 = None

            for item in sIter3:
                # CONVERT RA DEC TO DECIMAL DEGREES
                raSec = item.group('raSec')
                if item.group('raSubSec'):
                    raSec += item.group('raSubSec')
                decSec = item.group('decSec')
                if item.group('decSubSec'):
                    decSec += item.group('decSubSec')
                _raSex = """%s:%s:%s""" % (
                    item.group('raHrs'), item.group('raMin'), raSec)
                _decSex = """%s:%s:%s""" % (
                    item.group('decDeg'), item.group('decMin'), decSec)
                raDegrees = converter.ra_sexegesimal_to_decimal(
                    ra=_raSex
                )
                decDegrees = converter.dec_sexegesimal_to_decimal(
                    dec=_decSex
                )

                sList.extend([[str(raDegrees), str(decDegrees)]])
                userText = userText.replace(
                    item.group('raSex'), " **<font color=#dc322f>" + item.group('raSex') + " </font>** ")
                userText = userText.replace(
                    item.group('decSex'), " **<font color=#dc322f>" + item.group('decSex') + " </font>** ")

            numCoords = len(sList)

            # SEARCH FOR NAMES IN THE ATEL BODY
            try:
                sIter4 = reName.finditer(header)
            except:
                sIter4 = None
            try:
                sIter5 = reName.finditer(userText)
            except:
                sIter5 = None

            hnList = []
            for item in sIter4:
                hnList.extend([item.group()])
            hnList = list(set(hnList))
            numHeaderName = len(hnList)

            tnList = []
            for item in sIter5:
                tnList.extend([item.group()])
            tnList = list(set(tnList))
            numTextName = len(tnList)
            nList = list(set(hnList + tnList))

            # CLEAN UP THE NAMES BEFORE INGEST
            for i in range(len(nList)):
                nList[i] = clean_supernova_name(self.log, nList[i])
            nList = list(set(nList))

            userText = reName.sub(
                r"**<font color=#2aa198>\1</font>**", userText)
            header = reName.sub(
                r"**<font color=#2aa198>\1</font>**", header)

            # DETERMINE THE ATEL TYPE - DISCOVERY, CLASSIFICATION OR
            # OBSERVATION
            disc, obs, clas, correction, comment = 0, 0, 0, 0, 0
            discHead, obsHead, clasHead, correctionHead = 0, 0, 0, 0
            discText, obsText, clasText = 0, 0, 0

            # SEARCH FOR DISCOVERY KEYWORDS IN HEADER AND TEXT
            dList = []
            reDisc = re.compile(
                r"""(discovered\sby\sMASTER|Detection.{1,20}MASTER|detection\sof\sa\snew\s|discovery|candidate.{1,10}discovered|\ba\s?candidate|\d{1,4}:\s((Bright|MASTER)\sPSN\sin|Possible\snew\s|(A\s)?new.{1,30}(candidate|discovered)|(Bright|MASTER).{1,20}detection))""", re.I | re.M)
            reDiscPhrase = re.compile(
                r"""(We\sreport\sthe\sdiscovery\s)""", re.I)
            try:
                dpIter = reDiscPhrase.finditer(userText)
            except:
                dpIter = None
            for item in dpIter:
                # MIGHT AS WELL BE IN THE HEADER - IF reDiscPhrase AT START OF ATEL,
                # DEFINITELY A DISCOVERY
                discHead = 1
                dList.extend([item.group()])

            try:
                dhIter = reDisc.finditer(header)
            except:
                dhIter = None
            for item in dhIter:
                discHead = 1
                dList.extend([item.group()])

            try:
                dtIter = reDisc.finditer(userText)
            except:
                dtIter = None
            for item in dtIter:
                discText = 1
                dList.extend([item.group()])

            dList = list(set(dList))
            if len(dList) > 0:
                try:
                    userText = reDiscPhrase.sub(
                        r"**<font color=#b58900>\1</font>**", userText)
                except:
                    pass
                try:
                    userText = reDisc.sub(
                        r"**<font color=#b58900>\1</font>**", userText)
                except:
                    pass
                try:
                    header = reDisc.sub(
                        r"**<font color=#b58900>\1</font>**", header)
                except:
                    pass

            # SEARCH FOR CLASSIFICATION KEYWORDS IN HEADER AND TEXT
            cList = []
            reClass = re.compile(
                r'(classification|SNID|spectroscopic\sconfirmation|GELATO|discovery.*?SN\sI[abcilps]{1,3}n?)', re.I)
            try:
                chIter = reClass.finditer(header)
            except:
                chIter = None
            for item in chIter:
                clasHead = 1
                cList.extend([item.group()])
            try:
                ctIter = reClass.finditer(userText)
            except:
                ctIter = None
            for item in ctIter:
                clasText = 1
                cList.extend([item.group()])

            reClass2 = re.compile(
                r'(\sis\sa\s|SN\simpostor|type\sI[abcilps]{0,3}n?|\sI[abcilps]{0,3}n?\ssupernova|\sa\sSN\sI[abcilps]{0,3}n?)', re.I)
            try:
                cIter2 = reClass2.finditer(header)
            except:
                cIter2 = None
            for item in cIter2:
                clasHead = 1
                cList.extend([item.group()])

            cList = list(set(cList))
            if len(cList) > 0:
                try:
                    userText = reClass.sub(
                        r"**<font color=#b58900>\1</font>**", userText)
                except:
                    pass
                try:
                    header = reClass.sub(
                        r"**<font color=#b58900>\1</font>**", header)
                except:
                    pass
                try:
                    header = reClass2.sub(
                        r"**<font color=#b58900>\1</font>**", header)
                except:
                    pass

            # SEARCH FOR OBSERVATION KEYWORDS IN HEADER AND TEXT
            oList = []
            reObs = re.compile(
                r'(observations?|Outburst\sof\s|increase\sin\sflux\s|Progenitor\sIdentification|observed?|detects|new\soutburst|monitoring\sof)', re.I)
            try:
                ohIter = reObs.finditer(header)
            except:
                ohIter = None
            for item in ohIter:
                obsHead = 1
                oList.extend([item.group()])
            try:
                otIter = reObs.finditer(userText)
            except:
                otIter = None
            for item in otIter:
                obsText = 1
                oList.extend([item.group()])

            oList = list(set(oList))
            if len(oList) > 0:
                try:
                    userText = reObs.sub(
                        r"**<font color=#b58900>\1</font>**", userText)
                except:
                    pass
                try:
                    header = reObs.sub(
                        r"**<font color=#b58900>\1</font>**", header)
                except:
                    pass

            # SEARCH FOR CORRECTION KEYWORDS IN HEADER AND TEXT
            tList = []
            reCor = re.compile(r'((Correction|Erratum|Errata)\sto)', re.I)
            try:
                tIter = reCor.finditer(userText + header)
            except:
                tIter = None
            for item in tIter:
                tList.extend([item.group()])

            tList = list(set(tList))
            if len(tList) > 0:
                correctionHead = 1
                try:
                    userText = reCor.sub(
                        r"**<font color=#b58900>\1</font>**", userText)
                except:
                    pass
                try:
                    header = reCor.sub(
                        r"**<font color=#b58900>\1</font>**", header)
                except:
                    pass

            if "Comment" in tags:
                comment = 1

            # CREATE AN ATELTYPE TAG -- SIMPLE ROUTINE TO GUESS THE 'TYPE' OF
            # ATEL
            atelType = ""
            obs, clas, disc, correction = 0, 0, 0, 0
            # GIVE HEADER KEYWORDS PRIORITY OVER THE BODY TEXT
            if clasHead == 1:
                clas = 1
            if obsHead == 1:
                obs = 1
            if discHead == 1:
                disc = 1
            if correctionHead == 1:
                correction = 1
            if comment == 1:
                comment = 1

            if clasText == 1 and disc == 0 and obs == 0:
                clas = 1
            if obsText == 1 and disc == 0 and clas == 0:
                obs = 1
            if discText == 1 and obs == 0 and clas == 0:
                disc = 1

            if comment == 1:
                comment = 1

            if comment == 1:
                atelType += " comment "
            if correction == 1:
                atelType += " correction "
            if disc == 1:
                atelType += " discovery "
            if clas == 1:
                atelType += " classification "
            if obs == 1:
                atelType += " observation "

            # if atelType:
            # atelType = " || **<font color=#b58900>" + atelType + " </font>**
            # "
            header = header + atelType

            # IF THE ATEL-TYPE IS CLASSIFICATION THEN LOOK FOR THE
            # CLASSIFICATION
            SNTypeList = []
            SNTypeReplace = []
            singleClassification = None
            oneType = None
            if "classification" in atelType:
                try:
                    SNTypeIter = reSNType.finditer(header + userText)
                except:
                    SNTypeIter is None

                for item in SNTypeIter:
                    SNTypeReplace.extend([item.group()])
                    SNTypeList.extend([item.group(1)])
                    SNTypeList.extend([item.group(2)])
                    SNTypeList.extend([item.group(4)])
                    SNTypeList.extend([item.group(5)])
                    SNTypeList.extend([item.group(6)])
                    SNTypeList.extend([item.group(8)])
                SNTypeList = list(set(SNTypeList))
                SNTypeReplace = list(set(SNTypeReplace))

                for item in SNTypeReplace:
                    userText = userText.replace(
                        item, " ***<font color=#859900>" + item + " </font>*** ")
                    header = header.replace(
                        item, " ***<font color=#859900>" + item + " </font>*** ")

                switch = 0
                for item in SNTypeList:
                    if item:
                        if switch == 0:
                            oneType = item
                            switch = 1
                        else:
                            oneType = None
                        header = header + " ***<font color=#859900>" + \
                            item + " </font>*** "

            if not atelType:
                atelType = "observation"

            dateParsed = times.get_now_sql_datetime()

            sqlQuery = u"""
                            UPDATE atel_fullcontent
                            SET atelType = "%s",
                            dateParsed = "%s"
                            WHERE atelNUmber = %s
                        """ % (atelType.strip(), dateParsed, atelNumber,)

            writequery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn,
                Force=False
            )

            isSN = 0
            if "Supernovae" in tags:
                isSN = 1

                # PROVIDE THE SINGLE CLASSIFICATION IF THERE IS ONLY ONE GIVEN
                if oneType is not None:
                    singleClassification = oneType
                else:
                    singleClassification = None

            for item in sList:
                # CREATE AN ATEL 'NAME' & URL USEFUL FOR INGEST
                atelName = "atel_" + str(atelNumber)
                atelUrl = "http://www.astronomerstelegram.org/?read=" + \
                    str(atelNumber)
                survey = "atel-coords"
                sqlQuery = """INSERT INTO atel_coordinates (
                                                atelNumber,
                                                atelName,
                                                atelUrl,
                                                survey,
                                                raDeg,
                                                decDeg,
                                                supernovaTag
                                            )
                        VALUES (
                                    %s,
                                    "%s",
                                    "%s",
                                    "%s",
                                    %s,
                                    %s,
                                    %s
                                )""" % (atelNumber, atelName, atelUrl, survey, item[0], item[1], isSN)

                writequery(
                    log=self.log,
                    sqlQuery=sqlQuery,
                    dbConn=self.dbConn
                )

                if singleClassification is not None:
                    sqlQuery = """UPDATE atel_coordinates
                                    SET singleClassification = "%s"
                                    WHERE atelNumber = %s""" % (singleClassification, atelNumber,)

                    writequery(
                        log=self.log,
                        sqlQuery=sqlQuery,
                        dbConn=self.dbConn
                    )

            for item in nList:
                # CREATE AN ATEL 'NAME' & URL USEFUL FOR INGEST
                atelName = "atel_" + str(atelNumber)
                atelUrl = "http://www.astronomerstelegram.org/?read=" + \
                    str(atelNumber)
                survey = "atel-names"
                sqlQuery = """INSERT INTO atel_names (
                                                atelNumber,
                                                atelName,
                                                atelUrl,
                                                survey,
                                                name,
                                                supernovaTag
                                            )
                        VALUES (
                                    %s,
                                    "%s",
                                    "%s",
                                    "%s",
                                    "%s",
                                    %s
                        )""" % (atelNumber, atelName, atelUrl, survey, item, isSN)

                writequery(
                    log=self.log,
                    sqlQuery=sqlQuery,
                    dbConn=self.dbConn
                )

                if singleClassification is not None:
                    sqlQuery = """UPDATE atel_names
                                    SET singleClassification = "%s"
                                    WHERE atelNumber = %s""" % (singleClassification, atelNumber,)

                    writequery(
                        log=self.log,
                        sqlQuery=sqlQuery,
                        dbConn=self.dbConn
                    )

        self.log.debug('completed the ``parse_atels`` method')
        return None


def clean_supernova_name(log, snName):
    """
    *Clean a SN name. As a string, this function will attempt to clean up the name so that it is somewhat homogeneous with SN/transient from the same survey/atel system.*

    **Key Arguments:**
        - ``log`` -- logger
        - ``snName`` -- sn name to be cleaned (string)

    **Return:**
        - ``snName`` -- cleaned sn name (string)
    """

    # convert bytes to unicode
    if isinstance(snName, str):
        snName = unicode(snName, encoding="utf-8", errors="replace")

    snName = snName.replace(" ", "")
    snName = snName.replace(u"–", "-")
    snName = snName.replace("FSRQ", "")
    snName = snName.replace("Catalogue", "-")
    regex = re.compile(r'swift|css|sss|mls|master|^sn', re.I)
    if regex.search(snName):
        snName = regex.sub(regex.search(snName).group().upper(), snName)
    snName = snName.replace("SDSSgalaxy", "SDSS")
    snName = snName.replace('MASTERShort', "MASvTER")
    snName = snName.replace('MASTEROT', "MASTER")
    reMaster = re.compile(r'MASTER([^J])')
    snName = reMaster.sub('MASTERJ\g<1>', snName)
    regex = re.compile(r'SN.LSQ', re.I)
    snName = regex.sub('LSQ', snName)
    regex = re.compile(r'supernova', re.I)
    snName = regex.sub('SN', snName)
    regex = re.compile(r'GuideStarCatalog', re.I)
    snName = regex.sub('GSC-', snName)
    regex = re.compile(r'sdssgalaxy', re.I)
    snName = regex.sub('SDSS', snName)

    return snName
