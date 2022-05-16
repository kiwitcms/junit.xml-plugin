# Copyright (c) 2019-2022 Alexander Todorov <atodorov@MrSenko.com>

# Licensed under the GPLv3: https://www.gnu.org/licenses/gpl.html

from junitparser import Error, Failure, JUnitXml, Skipped
from tcms_api import plugin_helpers

from .version import __version__


class Backend(plugin_helpers.Backend):
    name = "kiwitcms-junit.xml-plugin"
    version = __version__


class Plugin:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.backend = Backend(prefix='[junit.xml]')

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
            summary = f"{xml_case.classname}.{xml_case.name}"[:255]

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
    if len(argv) < 2:
        program_name = argv[0]
        raise Exception(f"USAGE: {program_name} junit.xml")

    plugin = Plugin()
    plugin.parse(argv[1])
