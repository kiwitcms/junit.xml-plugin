# Copyright (c) 2019 Alexander Todorov <atodorov@MrSenko.com>

# Licensed under the GPLv3: https://www.gnu.org/licenses/gpl.html

from tcms_api.plugin_helpers import Backend


class Plugin:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.backend = Backend()

    def parse(self, junit_file, progress_cb=None):
        self.backend.configure()

        # parsing goes here
        #    if progress_cb:
        #        progress_cb()


def main(argv):
    if len(argv) < 2:
        raise Exception("USAGE: %s junit.xml" % argv[0])

    plugin = Plugin()
    plugin.parse(argv[1])
