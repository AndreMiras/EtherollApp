import os

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from etheroll.utils import SubScreen, load_kv_from_py
from version import __version__

load_kv_from_py(__file__)


class AboutOverview(BoxLayout):
    project_page_property = StringProperty(
        "https://github.com/AndreMiras/EtherollApp")
    about_text_property = StringProperty()

    def __init__(self, **kwargs):
        super(AboutOverview, self).__init__(**kwargs)
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
        super(AboutChangelog, self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.load_changelog())

    @staticmethod
    def src_dir():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    def load_changelog(self):
        changelog_path = os.path.join(self.src_dir(), 'CHANGELOG.md')
        with open(changelog_path, 'r') as f:
            self.changelog_text_property = f.read()
        f.close()


class AboutScreen(SubScreen):
    pass
