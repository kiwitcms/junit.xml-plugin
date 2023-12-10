# Copyright (c) 2019-2023 Alexander Todorov <atodorov@MrSenko.com>
# Licensed under the GPLv3: https://www.gnu.org/licenses/gpl.html
import argparse
from datetime import datetime
from datetime import timedelta
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

    @staticmethod
    def extract_logs(xml_case):
        return f"""

-----
Output logs:
```
{xml_case.system_out}
```

-----
Error logs:
```
{xml_case.system_err}
```
"""

    def testcase_summary(self, xml_suite, xml_case):
        """
        This method will generate the TestCase summary which is sent to
        Kiwi TCMS. It may be overriden for more flexibility!
        """
        values = {
            "classname": xml_case.classname,
            "name": xml_case.name,
            "suitename": getattr(xml_suite, "name", None),
        }
        return Template(self.summary_template).substitute(values)

    # pylint: disable=protected-access
    def testexecution_timestamps(self, xml_suite, xml_case):
        """
        This method will return (start_date, stop_date) if information
        is present!
        """
        start_date = None
        stop_date = None

        # some runners, e.g. Mocha.js reports a single starting timestamp
        # as a <testsuite> attribute. Take that if available!
        if "timestamp" in xml_suite._elem.attrib:
            start_date = self.parse_timestamp(xml_suite._elem.attrib["timestamp"])

        # update start_date if individual case contains this information
        if "timestamp" in xml_case._elem.attrib:
            start_date = self.parse_timestamp(xml_case._elem.attrib["timestamp"])
        if start_date and "time" in xml_case._elem.attrib:
            stop_date = start_date + timedelta(seconds=xml_case.time)

        return (start_date, stop_date)

    def parse_timestamp(self, value):
        """
        Try different timestamp formats until one of them finally works!
        """
        # IMPORTANT: keep the format strings ordered such that the parser extracts
        # as much information as possible
        for format_string in [
            "%Y-%m-%dT%H:%M:%S.%f",  # Nose2
            "%Y-%m-%dT%H:%M:%S",  # Mocha.js
            "%Y-%m-%d %H:%M:%S",  # Katalon Studio
        ]:
            try:
                return datetime.strptime(value, format_string)
            except ValueError:
                pass

        raise ValueError(f"Unknown timestamp format {value}")

    def parse_as_testsuites(self, xml_path):
        xml = JUnitXml.fromfile(xml_path)
        # apparently junit.xml may contain either a <testsuites> tag,
        # e.g. Katalon Studio, Mocha.js
        if xml._tag == "testsuites":  # pylint: disable=protected-access
            return xml

        # or a single <testsuite> tag,
        # e.g. Nose2, py.test
        if xml._tag == "testsuite":  # pylint: disable=protected-access
            # transforms the input data to a format which contains the <testsuites> tag
            new_xml = JUnitXml()
            # see JUnitXml.__iadd__() method
            new_xml += xml
            return new_xml

        raise RuntimeError(f"Unknown XML root tag {xml._tag}")

    def parse(
        self, junit_filenames, progress_cb=None
    ):  # pylint: disable=too-many-branches, too-many-locals
        self.backend.configure()

        for junit_xml in junit_filenames:
            if self.verbose:
                print(f"Parsing {junit_xml} ...")

            xml = self.parse_as_testsuites(junit_xml)

            for xml_suite in xml:
                for xml_case in xml_suite:
                    summary = self.testcase_summary(xml_suite, xml_case)[:255]

                    test_case, _ = self.backend.test_case_get_or_create(summary)
                    self.backend.add_test_case_to_plan(
                        test_case["id"], self.backend.plan_id
                    )

                    comment = self.backend.created_by_text
                    if not xml_case.result:
                        status_id = self.backend.get_status_id("PASSED")

                    # note: since junitpartser v2.0 the result attribute holds
                    # a list of values b/c pytest can produce files which contain
                    # multiple results for the same test case. We take the first!
                    for result in xml_case.result:
                        comment = result.tostring().decode().strip()
                        comment = f"```{comment}```"

                        if isinstance(result, Failure):
                            status_id = self.backend.get_status_id("FAILED")
                            comment += self.extract_logs(xml_case)
                            break

                        if isinstance(result, Error):
                            status_id = self.backend.get_status_id("ERROR")
                            comment += self.extract_logs(xml_case)
                            break

                        if isinstance(result, Skipped):
                            status_id = self.backend.get_status_id("WAIVED")
                            comment = result.message
                            break

                    for execution in self.backend.add_test_case_to_run(
                        test_case["id"],
                        self.backend.run_id,
                    ):
                        start_date, stop_date = self.testexecution_timestamps(
                            xml_suite, xml_case
                        )
                        self.backend.update_test_execution(
                            execution["id"],
                            status_id,
                            comment=comment,
                            start_date=start_date,
                            stop_date=stop_date,
                        )

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
    parser.add_argument(
        "filename.xml", type=str, nargs="+", help="XML file(s) to parse"
    )

    args = parser.parse_args(argv[1:])

    plugin = Plugin(verbose=args.verbose, summary_template=args.summary_template)
    plugin.parse(getattr(args, "filename.xml"))
