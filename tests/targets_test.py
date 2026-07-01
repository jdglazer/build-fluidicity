import unittest
from unittest.mock import MagicMock

from build_fluidicity_jdglazer.targets import BuildTarget

class TestBuildTarget(unittest.TestCase):

    def test_values_set(self):
        TARGET_NAME = "my-target"
        DESCRIPTION = "this is my description"
        target = BuildTarget(build=lambda: None, name=TARGET_NAME, description=DESCRIPTION)

        self.assertEqual(target.name, TARGET_NAME)
        self.assertEqual(target.description, DESCRIPTION)

    def test_build_function_called(self):
        build_func_mock = MagicMock()
        target = BuildTarget(build=build_func_mock, name="")
        target.build()
        build_func_mock.assert_called_once()

    def test_cleanup_function_called_on_exception(self):
        build_func_mock = MagicMock(side_effect=Exception(""))
        cleanup_func_mock = MagicMock()
        target = BuildTarget(build=build_func_mock, cleanup=cleanup_func_mock, name="")
        self.assertRaises(Exception, target.build)
        cleanup_func_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()