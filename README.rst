sublime-harness
===============

.. image:: https://travis-ci.org/twolfson/sublime-harness.png?branch=master
   :target: https://travis-ci.org/twolfson/sublime-harness
   :alt: Build Status

Run Python in Sublime Text from outside of Sublime Text

Getting Started
---------------
Install the module with: ``pip install sublime_harness``

.. code:: python

    import os, time
    from sublime_harness import sublime_harness

    harness = sublime_harness.Harness()
    script = """
    import sublime

    # Harness will run the `run` function
    def run():
        with open('/tmp/hi', 'w') as f:
            f.write('Hello World!')
        sublime.run_command('exit')"""
    harness.run(script)

    # Wait for our file to exist (Sublime Text is forked and not synchronous)
    while (not os.path.exists(output_file) or
           os.stat(output_file).st_size == 0):
        time.sleep(0.1)

    # Read our data
    with open('/tmp/hi') as f:
      print f.read()  # Hello World!

Documentation
-------------
_(Coming soon)_

Examples
--------
_(Coming soon)_

Contributing
------------
In lieu of a formal styleguide, take care to maintain the existing coding style. Add unit tests for any new or changed functionality. Test via ``nosetests``.

Donating
--------
Support this project and `others by twolfson`_ via `gittip`_.

.. image:: https://rawgithub.com/twolfson/gittip-badge/master/dist/gittip.png
   :target: `gittip`_
   :alt: Support via Gittip

.. _`others by twolfson`:
.. _gittip: https://www.gittip.com/twolfson/

Unlicense
---------
As of Oct 16 2013, Todd Wolfson has released this repository and its contents to the public domain.

It has been released under the `UNLICENSE`_.

.. _UNLICENSE: https://github.com/twolfson/sublime-harness/blob/master/UNLICENSE
