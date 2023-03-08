# Copyright (c) 2019-2022 Alexander Todorov <atodorov@MrSenko.com>

# Licensed under the GPLv3: https://www.gnu.org/licenses/gpl.html
import argparse

from junitparser import Error, Failure, JUnitXml, Skipped
from string import Template
from tcms_api import plugin_helpers

from .version import __version__


class Backend(plugin_helpers.Backend):
    name = "kiwitcms-junit.xml-plugin"
    version = __version__


class Plugin:  # pylint: disable=too-few-public-methods
    def __init__(self, summary_template, verbose=False):
        self.backend = Backend(prefix='[junit.xml]', verbose=verbose)
        self.summary_template = summary_template
        self.verbose = verbose

    def parse(
        self,
        junit_filenames,
        progress_cb=None
    ):  # pylint: disable=too-many-branches, too-many-locals
        self.backend.configure()

        for junit_xml in junit_filenames:
            if self.verbose:
                print(f"Parsing {junit_xml} ...")

            xml = JUnitXml.fromfile(junit_xml)
            # apparently junit.xml may contain either a <testsuites> tag,
            # e.g. Katalon Studio
            if xml._tag == "testsuites":  # pylint: disable=protected-access
                cases = []
                for suite in xml:
                    for case in suite:
                        cases.append(case)
            # or directly <testsuite> (only 1) tag - nose & py.test
            else:
                cases = list(xml)

            summary_template = Template(self.summary_template)
            for xml_case in cases:
                # Only permit non-secret values in this map
                # Users with template control can retrieve any value set here.
                values = {"classname": xml_case.classname, "name": xml_case.name}

                summary = summary_template.substitute(values)[:255]

                test_case, _ = self.backend.test_case_get_or_create(summary)
                self.backend.add_test_case_to_plan(test_case['id'],
                                                   self.backend.plan_id)

                comment = self.backend.created_by_text
                if not xml_case.result:
                    status_id = self.backend.get_status_id('PASSED')

                # note: since junitpartser v2.0 the result attribute holds
                # a list of values b/c pytest can produce files which contain
                # multiple results for the same test case. We take the first!
                for result in xml_case.result:
                    if isinstance(result, Failure):
                        status_id = self.backend.get_status_id('FAILED')
                        comment = result.tostring()
                        break

                    if isinstance(result, Error):
                        status_id = self.backend.get_status_id('ERROR')
                        comment = result.tostring()
                        break

                    if isinstance(result, Skipped):
                        status_id = self.backend.get_status_id('WAIVED')
                        comment = result.message
                        break

                for execution in self.backend.add_test_case_to_run(
                    test_case['id'],
                    self.backend.run_id,
                ):
                    self.backend.update_test_execution(execution["id"],
                                                       status_id,
                                                       comment)

                if progress_cb:
                    progress_cb()

        self.backend.finish_test_run()


def main(argv):
    parser = argparse.ArgumentParser(
        description='Parse the specified XML files and '
                    'send the results to Kiwi TCMS'
    )
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Print information about created TP/TR records')
    parser.add_argument('--summary-template', dest='summary_template', type=str,
                        help='Template to convert testcase to summary, eg %(default)s.',
                        default='${classname}.${name}')
    parser.add_argument('filename.xml', type=str, nargs='+',
                        help='XML file(s) to parse')

    args = parser.parse_args(argv[1:])

    plugin = Plugin(args.summary_template, verbose=args.verbose)
    plugin.parse(getattr(args, 'filename.xml'))
