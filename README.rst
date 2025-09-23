junit.xml plugin for Kiwi TCMS
==============================

.. image:: https://img.shields.io/pypi/v/kiwitcms-junit.xml-plugin.svg
    :target: https://pypi.org/project/kiwitcms-junit.xml-plugin
    :alt: PyPI version

.. image:: https://travis-ci.org/kiwitcms/junit.xml-plugin.svg?branch=master
    :target: https://travis-ci.org/kiwitcms/junit.xml-plugin
    :alt: Travis CI

.. image:: https://coveralls.io/repos/github/kiwitcms/junit.xml-plugin/badge.svg?branch=master
    :target: https://coveralls.io/github/kiwitcms/junit.xml-plugin?branch=master
    :alt: Code coverage

.. image:: https://pyup.io/repos/github/kiwitcms/junit.xml-plugin/shield.svg
    :target: https://pyup.io/repos/github/kiwitcms/junit.xml-plugin/
    :alt: Python updates

.. image:: https://img.shields.io/badge/kiwi%20tcms-results-9ab451.svg
    :target: https://tcms.kiwitcms.org/plan/7/
    :alt: TP for kiwitcms/junit.xml-plugin (master)

.. image:: https://tidelift.com/badges/package/pypi/kiwitcms-junit.xml-plugin
    :target: https://tidelift.com/subscription/pkg/pypi-kiwitcms-junit.xml-plugin?utm_source=pypi-kiwitcms-junit.xml-plugin&utm_medium=github&utm_campaign=readme
    :alt: Tidelift

.. image:: https://opencollective.com/kiwitcms/tiers/sponsor/badge.svg?label=sponsors&color=brightgreen
   :target: https://opencollective.com/kiwitcms#contributors
   :alt: Become a sponsor

.. image:: https://img.shields.io/twitter/follow/KiwiTCMS.svg
    :target: https://twitter.com/KiwiTCMS
    :alt: Kiwi TCMS on Twitter


This package allows you to read junit.xml files and
send the results to `Kiwi TCMS <http://kiwitcms.org>`_.


Installation
------------

::

    pip install kiwitcms-junit.xml-plugin


Configuration and environment
-----------------------------

Minimal config file `~/.tcms.conf`::

    [tcms]
    url = https://tcms.server/xml-rpc/
    username = your-username
    password = your-password


For more info see `tcms-api docs <https://tcms-api.readthedocs.io>`_.

This plugin is only concerned with parsing the junit.xml format and executing
`tcms-api` functions which will create/reuse test cases, test plans and test runs.
`tcms-api` behavior is controlled via environment variables.

For example this is how our own environment looks like::

    #!/bin/bash

    if [ "$TRAVIS_EVENT_TYPE" == "push" ]; then
        # same as $TRAVIS_TAG when building tags
        export TCMS_PRODUCT_VERSION=$TRAVIS_BRANCH
    fi

    if [ "$TRAVIS_EVENT_TYPE" == "pull_request" ]; then
        export TCMS_PRODUCT_VERSION="PR-$TRAVIS_PULL_REQUEST"
    fi

    export TCMS_BUILD="$TRAVIS_BUILD_NUMBER-$(echo $TRAVIS_COMMIT | cut -c1-7)"

Further documentation and behavior specification can be found
`here <https://tcms-api.readthedocs.io/en/latest/modules/tcms_api.plugin_helpers.html>`_.

The above configuration creates a separate TestPlan for each branch, see
`TP-7: [junit.xml] Plan for kiwitcms/junit.xml-plugin (master) <https://tcms.kiwitcms.org/plan/7/>`_,
a separate TestPlan for each pull request (recording possible multiple test runs) and
separate TestPlan and TestRun for each tag on GitHub! `tcms-api` has default behavior
for Travis CI and Jenkins and allows endless configuration via environment variables.


Usage
-----

::

    # define environment variables
    tcms-junit.xml-plugin /path/to/junit.xml


Changelog
---------

v15.0 (23 Sep 2025)
~~~~~~~~~~~~~~~~~~~

- Update junitparser from 3.1.0 to 3.2.0
- Drop official support for Python 3.8


v12.8.1 (22 Dec 2023)
~~~~~~~~~~~~~~~~~~~~~

- Update tcms-api from 12.7 to 12.8.1
- Relax the requirement on tcms-api to allow for easier upgrades


v12.7 (10 Dec 2023)
~~~~~~~~~~~~~~~~~~~

- Update junitparser from 2.8.0 to 3.1.0
- Update tcms-api from 12.2 to 12.7
- Calculate ``stop_date`` only when ``start_date`` is valid (Michael Kaye)


v12.2.999 (18 Apr 2023)
~~~~~~~~~~~~~~~~~~~~~~~

- Read ``start_date`` from ``<testsuite timestamp>`` if it exists. Fixes
  `Issue #89 <https://github.com/kiwitcms/junit.xml-plugin/issues/89>`_
- Internal refactoring. **WARNING:** contains backwards incompatible changes for
  ``testcase_summary()`` and ``testexecution_timestamps()`` methods which will
  break inherited classes


v12.2 (04 Apr 2023)
~~~~~~~~~~~~~~~~~~~

- Report TestExecution timestamps if present in XML


v12.1 (21 Mar 2023)
~~~~~~~~~~~~~~~~~~~

- Decode byte strings before sending comments to RPC (Sergey Lazarev)
- Format comments as Markdown when rendering the raw XML values
- Append stdout/stderr information to failure/error comments
- Updates around CI and expanded test matrix


v12.0 (16 Mar 2023)
~~~~~~~~~~~~~~~~~~~

- Provide a ``--summary-template`` for optional customization of the
  summary generated from the test cases (Michael Kaye)
- Update junitparser from 2.5.0 to 2.8.0
- Update tcms-api from 11.3 to 11.4
- Refactoring and code formatting
- Add CodeQL workflow for GitHub code scanning


v11.3 (18 May 2022)
~~~~~~~~~~~~~~~~~~~

- Update tcms-api from 11.2 to 11.3
- Print information about created records if ``-v`` or ``--verbose``
  is specified on the command line
- Allow multiple XML files to be specified on the command line


v11.2 (16 May 2022)
~~~~~~~~~~~~~~~~~~~

- Update junitparser from 2.2.0 to 2.5.0
- Update tcms-api from 11.0 to 11.2
- Annotate plugin with name & version information
- Trim TestCase.summary to 255 characters. Fixes
  `Issue #44 <https://github.com/kiwitcms/junit.xml-plugin/issues/44>`_
- Updates around testing of this package


v11.0 (05 Dec 2021)
~~~~~~~~~~~~~~~~~~~

- Future compatible with upcoming Kiwi TCMS v11.0
- Update tcms-api to 11.0
- Update junitparser from 2.0.0 to 2.2.0
- Fix pylint issues


v10.0 (02 Mar 2021)
~~~~~~~~~~~~~~~~~~~

- Compatible with Kiwi TCMS v10.0
- Update tcms-api to 10.0


v9.0 (13 Jan 2021)
~~~~~~~~~~~~~~~~~~

- Compatible with Kiwi TCMS v9.0
- Update tcms-api to 9.0
- Update junitparser to 2.0.0
- Adjusted code to handle jUnit v2.0 files


v8.4 (28 Oct 2020)
~~~~~~~~~~~~~~~~~~

- Update tcms-api to 8.6.0
- Update junitparser to 1.6.0


v8.3 (10 Apr 2020)
~~~~~~~~~~~~~~~~~~

- Update to
  `tcms-api v8.3.0 <https://github.com/kiwitcms/tcms-api/#v830-10-april-2020>`_
  which uses ``gssapi`` for Kerberos
- Requires MIT Kerberos for Windows if installed on Windows


v8.2 (03 Apr 2020)
~~~~~~~~~~~~~~~~~~

This version works only with Kiwi TCMS v8.2 or later!

- Update to tcms-api==8.2.0
- Patch for changed return value in
  ``plugin_helpers.Backend.test_case_get_or_create()``
- Call ``plugin_helpers.backend.finish_test_run()`` when done


v8.0.1 (10 February 2020)
~~~~~~~~~~~~~~~~~~~~~~~~~

This version works only with Kiwi TCMS v8.0 or later!

- Adjust plugin due to API changes in Kiwi TCMS v8.0
- Require tcms-api==8.0.1


v0.5 (07 January 2020)
~~~~~~~~~~~~~~~~~~~~~~

- Update junitparser from 1.3.4 to 1.41


v0.4 (20 September 2019)
~~~~~~~~~~~~~~~~~~~~~~~~

- Update junitparser from 1.3.2 to 1.3.4
- Support XML files with <testsuites> root tag (Katalon Studio).
  Fixes `Issue #9 <https://github.com/kiwitcms/junit.xml-plugin/issues/9>`_


v0.3 (10 April 2019)
~~~~~~~~~~~~~~~~~~~~

- Works with Kiwi TCMS v6.7 or newer
- Uses new names of API methods
