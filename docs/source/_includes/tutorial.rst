Command-Line Tutorial
=====================

Before you begin using atelParser you will need to populate some custom settings within the atelParser settings file.

To setup the default settings file at ``~/.config/atelParser/atelParser.yaml`` run the command:

.. code-block:: bash 
    
    > atel init

This should create and open the settings file; follow the instructions in the file to populate the missing settings values (usually given an ``XXX`` placeholder). 

Report the Latest ATel Count
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To report the latest ATel count run the command:

.. code-block:: bash

    > atel count
    11994 ATels have been reported as of 2018/08/29 13:31:02s

Downloading all new ATels
~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have an ``atel-directory`` parameter added to your settings file you can download all missign ATels to this directory.

.. code-block:: yaml 
    
    atel-directory: /home/user/atel-archive/html 

To kick off the download run the command:

.. code-block:: bash 
    
    atel download

This will download the HTML pages for all new/missing ATels to your ``atel-directory``.
