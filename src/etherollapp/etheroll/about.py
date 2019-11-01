import os

from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from etherollapp.etheroll.ui_utils import SubScreen, load_kv_from_py
from etherollapp.etheroll.utils import StringIOCBWrite, run_in_thread
from etherollapp.version import __version__

load_kv_from_py(__file__)


class AboutOverview(BoxLayout):
    project_page_property = StringProperty(
        "https://github.com/AndreMiras/EtherollApp")
    about_text_property = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.load_about())

    def load_about(self):
        self.about_text_property = "" + \
            "EtherollApp version: %s\n" % (__version__) + \
            "Project source code and info available on GitHub at:\n" + \
            "[color=00BFFF][ref=github]" + \
            self.project_page_property + \
            "[/ref][/color]"


class AboutChangelog(BoxLayout):
    changelog_text_property = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.load_changelog())

    @staticmethod
    def src_dir():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    def load_changelog(self):
        changelog_path = os.path.join(self.src_dir(), 'CHANGELOG.md')
        with open(changelog_path, 'r') as f:
            self.changelog_text_property = f.read()
        f.close()


class AboutDiagnostic(BoxLayout):
    stream_property = StringProperty()

    @mainthread
    def callback_write(self, s):
        """Updates the UI with test progress."""
        self.stream_property += s

    @run_in_thread
    def run_tests(self):
        """Loads the test suite and hook the callback for progress report."""
        # lazy loading
        import unittest
        from etherollapp.testsuite import suite
        test_suite = suite()
        self.stream_property = ""
        stream = StringIOCBWrite(callback_write=self.callback_write)
        verbosity = 2
        unittest.TextTestRunner(
                stream=stream, verbosity=verbosity).run(test_suite)


class AboutScreen(SubScreen):
    pass
