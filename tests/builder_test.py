import sys
import unittest
from typing import Dict, override
from unittest.mock import MagicMock, call

sys.path.append('.\\src')

from build_fluidicity.builder import BuildTargetLoader, Builder, BuildException, BuildTarget

class MockBuildTargetLoader(BuildTargetLoader):

    def __init__(self, build_targets: Dict[str, BuildTarget]):
        self.build_targets = build_targets

    @override
    def load_available_build_targets(self):
        return self.build_targets

class TestBuilder(unittest.TestCase):

    TARGET_NAME_BASE = ["createdirs", "downloadfiles", "convertfiles", "runtilemaker"]
    LOADED_TARGET_BASE: Dict[str, BuildTarget] = {
            "createdirs": BuildTarget(name="createdirs", build=lambda: None),
            "downloadfiles": BuildTarget(name="downloadfiles", build=lambda: None),
            "convertfiles": BuildTarget(name="convertfiles", build=lambda: None)
    }

    def test_no_duplicate_targets_allowed(self):
        target_names = TestBuilder.TARGET_NAME_BASE + ["convertfiles"]

        self.assertRaises(BuildException, Builder([], MockBuildTargetLoader({}))._verify_targets_to_run, target_names)

    def test_top_level_target_existence_check(self):
        tree = Builder([], MockBuildTargetLoader(TestBuilder.LOADED_TARGET_BASE))

        self.assertRaises(BuildException, tree._verify_targets_to_run, TestBuilder.TARGET_NAME_BASE)

    def test_circular_dependency_check(self):
        loaded_targets = TestBuilder.LOADED_TARGET_BASE.copy()
        loaded_targets["createdirs"]._dependency_names = ["downloadfiles", "convertfiles"]
        loaded_targets["downloadfiles"]._dependency_names = ["createdirs"]

        self.assertRaises(BuildException, Builder, ["createdirs"], MockBuildTargetLoader(loaded_targets))

    def test_dependency_target_does_not_exist_check(self):
        loaded_targets = TestBuilder.LOADED_TARGET_BASE.copy()
        loaded_targets["createdirs"]._dependency_names = ["downloadfiles", "convertfiles"]
        del loaded_targets["convertfiles"]

        self.assertRaises(BuildException, Builder, ["createdirs"], MockBuildTargetLoader(loaded_targets))

    def test_load_build_success(self):
        loaded_targets = TestBuilder.LOADED_TARGET_BASE.copy()
        loaded_targets["createdirs"]._dependency_names = ["downloadfiles", "convertfiles"]
        loaded_targets["downloadfiles"]._dependency_names = ["convertfiles"]

        tree = None
        try:
            tree = Builder(["createdirs"], MockBuildTargetLoader(loaded_targets))
        except:
            pass

        self.assertIsNotNone(tree)

    def test_all_build_targets_run(self):
        mock = MagicMock()
        mock.build_func_one.return_value = None
        mock.build_func_two.return_value = None
        mock.build_func_three.return_value = None

        BUILD_TARGETS = {
            "one": BuildTarget(build=mock.build_func_one, name="one"),
            "two": BuildTarget(build=mock.build_func_two, name="two"),
            "three": BuildTarget(build=mock.build_func_three, name="three")
        }

        mock_target_loader = MockBuildTargetLoader(BUILD_TARGETS)

        builder = Builder(targets_to_run=["one", "two", "three"], target_loader=mock_target_loader)
        builder.run()

        mock.build_func_one.assert_called_once()
        mock.build_func_two.assert_called_once()
        mock.build_func_three.assert_called_once()

    def test_build_stops_after_exception(self):
        mock = MagicMock()
        mock.build_func_one.return_value = None
        mock.build_func_two.return_value = None
        mock.build_func_two.side_effect = Exception("")
        mock.build_func_three.return_value = None

        BUILD_TARGETS = {
            "one": BuildTarget(build=mock.build_func_one, name="one"),
            "two": BuildTarget(build=mock.build_func_two, name="two"),
            "three": BuildTarget(build=mock.build_func_three, name="three")
        }

        mock_target_loader = MockBuildTargetLoader(BUILD_TARGETS)

        builder = Builder(targets_to_run=["one", "two", "three"], target_loader=mock_target_loader)
        builder.run()

        mock.build_func_one.assert_called_once()
        mock.build_func_two.assert_called_once()
        mock.build_func_three.assert_not_called()

    def test_build_runs_correct_cleanup_after_fail(self):
        mock = MagicMock()

        mock.build_func_one.return_value = None
        mock.cleanup_func_one.return_value = None

        mock.build_func_two.return_value = None
        mock.cleanup_func_two.return_value = None
        mock.build_func_two.side_effect = Exception("")

        mock.build_func_three.return_value = None
        mock.cleanup_func_three.return_value = None

        BUILD_TARGETS = {
            "one": BuildTarget(build=mock.build_func_one, cleanup=mock.cleanup_func_one, name="one"),
            "two": BuildTarget(build=mock.build_func_two, cleanup=mock.cleanup_func_two, name="two"),
            "three": BuildTarget(build=mock.build_func_three, cleanup=mock.cleanup_func_three, name="three")
        }

        mock_target_loader = MockBuildTargetLoader(BUILD_TARGETS)

        builder = Builder(targets_to_run=["one", "two", "three"], target_loader=mock_target_loader)
        builder.run()

        mock.cleanup_func_one.assert_called_once()
        mock.cleanup_func_two.assert_called_once()
        # cleanup should not be called for targets that didn't yet run
        mock.cleanup_func_three.assert_not_called()

    def test_cleanup_doesnt_runs_after_complete_success(self):
        mock = MagicMock()

        mock.build_func_one.return_value = None
        mock.cleanup_func_one.return_value = None

        mock.build_func_two.return_value = None
        mock.cleanup_func_two.return_value = None

        mock.build_func_three.return_value = None
        mock.cleanup_func_three.return_value = None

        BUILD_TARGETS = {
            "one": BuildTarget(build=mock.build_func_one, cleanup=mock.cleanup_func_one, name="one"),
            "two": BuildTarget(build=mock.build_func_two, cleanup=mock.cleanup_func_two, name="two"),
            "three": BuildTarget(build=mock.build_func_three, cleanup=mock.cleanup_func_three, name="three")
        }

        mock_target_loader = MockBuildTargetLoader(BUILD_TARGETS)

        builder = Builder(targets_to_run=["one", "two", "three"], target_loader=mock_target_loader)
        builder.run()

        mock.cleanup_func_one.assert_not_called()
        mock.cleanup_func_two.assert_not_called()
        mock.cleanup_func_three.assert_not_called()

    def test_dependencies_run_in_correct_order(self):
        mock = MagicMock()

        mock.build_func_one.return_value = None
        mock.build_func_two.return_value = None
        mock.build_func_three.return_value = None
        mock.build_func_four.return_value = None
        mock.build_func_five.return_value = None
        mock.build_func_six.return_value = None

        BUILD_TARGETS = {
            "one": BuildTarget(build=mock.build_func_one, name="one", dependency_names=["two", "three"]),
            "two": BuildTarget(build=mock.build_func_two, name="two"),
            "three": BuildTarget(build=mock.build_func_three, name="three", dependency_names=["four"]),
            "four": BuildTarget(build=mock.build_func_four, name="four"),
            "five": BuildTarget(build=mock.build_func_five, name="five"),
            "six": BuildTarget(build=mock.build_func_six, name="six")
        }

        mock_target_loader = MockBuildTargetLoader(BUILD_TARGETS)

        builder = Builder(targets_to_run=["one", "five"], target_loader=mock_target_loader)
        builder.run()

        expected_calls = [
            call.build_func_two(),
            call.build_func_four(),
            call.build_func_three(),
            call.build_func_one(),
            call.build_func_five()
        ]

        mock.assert_has_calls(calls=expected_calls, any_order=False)
        mock.build_func_six.assert_not_called()


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
