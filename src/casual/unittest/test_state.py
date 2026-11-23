import os
import pprint
import unittest

from casual.make.entity import cli, settings


class TestState(unittest.TestCase):

    def test_dry_run(self):
        settings.get_settings().setup()
        arguments = cli.handle_arguments(["--dry-run"])
        settings.environment(arguments)
        self.assertEqual(settings.get_settings().dry_run(), True)
        self.assertEqual(settings.get_settings().raw_format(), False)

    def test_raw_format(self):
        settings.get_settings().setup()
        arguments = cli.handle_arguments(["--raw"])
        settings.environment(arguments)
        self.assertEqual(settings.get_settings().dry_run(), False)
        self.assertEqual(settings.get_settings().raw_format(), True)

    def test_source_root_git_value(self):
        settings.get_settings().setup()
        if "CASUAL_MAKE_SOURCE_ROOT" in os.environ:
            del os.environ["CASUAL_MAKE_SOURCE_ROOT"]

        arguments = cli.handle_arguments()
        settings.environment(arguments)
        env_source_root = os.path.normpath(os.getenv("CASUAL_MAKE_HOME") + "/..")
        self.assertEqual(settings.get_settings().source_root(), env_source_root)
        self.assertEqual(settings.get_settings().raw_format(), False)

    def test_source_root_use_variable(self):
        settings.get_settings().setup()
        arguments = cli.handle_arguments()
        answer = "testvalue"
        os.environ["CASUAL_MAKE_SOURCE_ROOT"] = answer
        settings.environment(arguments)

        self.assertEqual(settings.get_settings().source_root(), answer)
        self.assertEqual(settings.get_settings().raw_format(), False)


if __name__ == "__main__":
    pprint.pprint(os.environ)
    unittest.main()
