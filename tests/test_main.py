# pylint: disable=no-self-use
import unittest
from unittest.mock import patch

from tcms_junit_plugin import main


class MainFuncTestCase(unittest.TestCase):
    def test_when_calling_main_with_arguments_then_parse(self):
        with patch("tcms_junit_plugin.Plugin.parse") as parse:
            main([__file__, "junit.xml"])
            parse.assert_called_with(["junit.xml"])

    def test_when_calling_main_without_arguments_then_usage(self):
        with self.assertRaisesRegex(SystemExit, "2"):
            main([__file__])
