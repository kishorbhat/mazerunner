==========
mazerunner
==========

Game made for the `Escape the Trolls <https://www.reddit.com/r/dailyprogrammer/comments/4vrb8n/weekly_25_escape_the_trolls/>`_ challenge over at Reddit.

=======
Running
=======


.. code:: bash

    $ python mazerunner/mazerunner.py

**Note**: your terminal window must be large enough to accommodate the entire maze. Strange things happen otherwise.

Tips on running in Windows: 
    The curses module is not supported on Windows machines. 
    You can install the unofficial binary for curses from http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses.

==============
Generate Mazes
==============
To generate mazes, you will need to have numpy installed:

.. code:: bash

    $ pip install numpy


You can generate your own mazes using:

.. code:: bash

    $ python mazerunner/generate.py mazename.txt width height


======
Legend
======
T -- troll

^/>/v/^ -- player

X -- exit

# -- wall

=======
LICENSE
=======
MIT.

