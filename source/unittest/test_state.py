import unittest

import casual.make.entity.state as state
import casual.make.entity.cli as cli
import os

class TestState(unittest.TestCase):

    def test_dry_run(self):
        state.settings.clear()
        arguments = cli.handle_arguments(['--dry-run'])
        state.environment(arguments)
        self.assertEqual(state.settings.dry_run, True)
        self.assertEqual(state.settings.raw_format, False)

    def test_raw_format(self):
        state.settings.clear()
        arguments = cli.handle_arguments(['--raw'])
        state.environment(arguments)
        self.assertEqual(state.settings.dry_run, False)
        self.assertEqual(state.settings.raw_format, True)

    def test_source_root_git_value(self):
        state.settings.clear()
        if 'CASUAL_MAKE_SOURCE_ROOT' in os.environ:
            del os.environ['CASUAL_MAKE_SOURCE_ROOT']

        arguments = cli.handle_arguments()
        state.environment(arguments)
        self.assertEqual(state.settings.source_root, os.path.normpath(os.getenv("CASUAL_MAKE_HOME") + "/.."))
        self.assertEqual(state.settings.raw_format, False)

    def test_source_root_use_variable(self):
        state.settings.clear()
        arguments = cli.handle_arguments()
        answer = 'testvalue'
        os.environ['CASUAL_MAKE_SOURCE_ROOT'] = answer
        state.environment(arguments)

        self.assertEqual(state.settings.source_root, answer)
        self.assertEqual(state.settings.raw_format, False)


if __name__ == '__main__':
    unittest.main()