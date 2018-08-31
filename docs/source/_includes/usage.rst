Command-Line Usage
==================

.. code-block:: bash 
   
    
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
    
