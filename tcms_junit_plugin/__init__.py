# Copyright (c) 2019-2023 Alexander Todorov <atodorov@MrSenko.com>
# Licensed under the GPLv3: https://www.gnu.org/licenses/gpl.html
import argparse
from string import Template

from junitparser import Error
from junitparser import Failure
from junitparser import JUnitXml
from junitparser import Skipped
from tcms_api import plugin_helpers

from .version import __version__


DEFAULT_TEMPLATE = "${classname}.${name}"


class Backend(plugin_helpers.Backend):
    name = "kiwitcms-junit.xml-plugin"
    version = __version__


class Plugin:  # pylint: disable=too-few-public-methods
    def __init__(self, verbose=False, summary_template=DEFAULT_TEMPLATE):
        self.backend = Backend(prefix="[junit.xml]", verbose=verbose)
        self.verbose = verbose
        # NB: template is defaulted both here and in the argument parser below
        self.summary_template = summary_template

    def testcase_summary(self, xml_case):
        """
        This method will generate the TestCase summary which is sent to
        Kiwi TCMS. It may be overriden for more flexibility!
        """
        values = {
            "classname": xml_case.classname,
            "name": xml_case.name,
            "suitename": getattr(xml_case, "suitename", None),
        }
        return Template(self.summary_template).substitute(values)

    def parse(
        self, junit_filenames, progress_cb=None
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
                        # Retain the suite name (if present) with each
                        # testcase.
                        if suite.name:
                            case.suitename = suite.name
                        cases.append(case)
            # or directly <testsuite> (only 1) tag - nose & py.test
            else:
                cases = list(xml)

            for xml_case in cases:
                summary = self.testcase_summary(xml_case)[:255]

                test_case, _ = self.backend.test_case_get_or_create(summary)
                self.backend.add_test_case_to_plan(test_case["id"], self.backend.plan_id)

                comment = self.backend.created_by_text
                if not xml_case.result:
                    status_id = self.backend.get_status_id("PASSED")

                # note: since junitpartser v2.0 the result attribute holds
                # a list of values b/c pytest can produce files which contain
                # multiple results for the same test case. We take the first!
                for result in xml_case.result:
                    if isinstance(result, Failure):
                        status_id = self.backend.get_status_id("FAILED")
                        comment = result.tostring()
                        break

                    if isinstance(result, Error):
                        status_id = self.backend.get_status_id("ERROR")
                        comment = result.tostring()
                        break

                    if isinstance(result, Skipped):
                        status_id = self.backend.get_status_id("WAIVED")
                        comment = result.message
                        break

                for execution in self.backend.add_test_case_to_run(
                    test_case["id"],
                    self.backend.run_id,
                ):
                    self.backend.update_test_execution(execution["id"], status_id, comment)

                if progress_cb:
                    progress_cb()

        self.backend.finish_test_run()


def main(argv):
    parser = argparse.ArgumentParser(
        description="Parse the specified XML files and " "send the results to Kiwi TCMS"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Print information about created TP/TR records",
    )
    # NB: template is defaulted both here and in the Plugin init method above
    parser.add_argument(
        "--summary-template",
        dest="summary_template",
        type=str,
        help="Template summary from testcase, eg %(default)s.",
        default=DEFAULT_TEMPLATE,
    )
    parser.add_argument("filename.xml", type=str, nargs="+", help="XML file(s) to parse")

    args = parser.parse_args(argv[1:])

    plugin = Plugin(verbose=args.verbose, summary_template=args.summary_template)
    plugin.parse(getattr(args, "filename.xml"))
