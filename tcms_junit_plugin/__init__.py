# Copyright (c) 2019 Alexander Todorov <atodorov@MrSenko.com>

# Licensed under the GPLv3: https://www.gnu.org/licenses/gpl.html

from junitparser import Error, Failure, JUnitXml, Skipped
from tcms_api.plugin_helpers import Backend


class Plugin:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.backend = Backend(prefix='[junit.xml] ')

    def parse(self, junit_xml, progress_cb=None):
        self.backend.configure()

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

        for xml_case in cases:
            summary = "%s.%s" % (xml_case.classname, xml_case.name)

            test_case = self.backend.test_case_get_or_create(summary)
            test_case_id = test_case['case_id']

            self.backend.add_test_case_to_plan(test_case_id,
                                               self.backend.plan_id)

            test_execution_id = self.backend.add_test_case_to_run(
                test_case_id,
                self.backend.run_id)
            comment = 'Result recorded via Kiwi TCMS junit.xml-plugin'

            if xml_case.result is None:
                status_id = self.backend.get_status_id('PASSED')

            if isinstance(xml_case.result, Failure):
                status_id = self.backend.get_status_id('FAILED')
                comment = xml_case.result.tostring()

            if isinstance(xml_case.result, Error):
                status_id = self.backend.get_status_id('ERROR')
                comment = xml_case.result.tostring()

            if isinstance(xml_case.result, Skipped):
                status_id = self.backend.get_status_id('WAIVED')
                comment = xml_case.result.message

            self.backend.update_test_execution(test_execution_id,
                                               status_id,
                                               comment)

            if progress_cb:
                progress_cb()


def main(argv):
    if len(argv) < 2:
        raise Exception("USAGE: %s junit.xml" % argv[0])

    plugin = Plugin()
    plugin.parse(argv[1])
