sublime-harness
===============

.. image:: https://travis-ci.org/twolfson/sublime-harness.png?branch=master
   :target: https://travis-ci.org/twolfson/sublime-harness
   :alt: Build Status

Run Python in Sublime Text from outside of Sublime Text

``sublime-harness`` was built to allow for execution of arbitrary Python within the context of `Sublime Text`_. It is also part of the `Sublime plugin tests`_ framework.

.. _`Sublime Text`: http://sublimetext.com/
.. _`Sublime plugin tests`: https://github.com/twolfson/sublime-plugin-tests

    Currently, only Linux is supported but OSX and Windows support are planned.

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
``sublime_harness`` provides the ``Harness`` class for all your bootstrapping needs.

`Sublime Text`_ will be resolved via `sublime-info`_, which allows for overriding via environment variables.

.. _`sublime-info`: https://github.com/twolfson/sublime-info

Harness.__init__
^^^^^^^^^^^^^^^^
.. code:: python

    Harness()
    """Generate a new Harness for Sublime Text

    When initialized, `Harness` allocates a directory (currently, same for all harnesses) for your script.
    """

Harness.directory
^^^^^^^^^^^^^^^^
.. code:: python

    harness.directory
    """Directory where `run` will be execute

    If you would like to load relative modules, they should be copied to this directory."""

Harness.run
^^^^^^^^^^^
.. code:: python

    harness.run(script)
    """Python to execute within the context of Sublime Text

    **YOU MUST CLEAN UP AFTER RUNNING THIS METHOD VIA `close`**

    You can only run one harness at a time due to the lack of namespacing.

    :param script: Python to execute within Sublime Text
    :type script: str
    """

Harness.close
^^^^^^^^^^^
.. code:: python

    harness.close()
    """Cleans up harness files"""

Examples
--------
TODO: One with dictionary

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
