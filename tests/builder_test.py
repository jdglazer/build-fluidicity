import unittest
from typing import Dict
from unittest.mock import MagicMock, call

from build_fluidicity_jdglazer.builder import Builder
from build_fluidicity_jdglazer.loaders import BuildTargetLoader
from build_fluidicity_jdglazer.targets import BuildTarget, MetaBuildTarget

"""
    def test_build_function_called(self):
        build_func_mock = MagicMock()
        target = UltraSimpleBuildTargetSub(name="")
        target.build()
        build_func_mock.assert_called_once()

    def test_cleanup_function_called_on_exception(self):
        build_func_mock = MagicMock(side_effect=Exception(""))
        cleanup_func_mock = MagicMock()
        target = BuildTarget(build=build_func_mock, cleanup=cleanup_func_mock, name="")
        self.assertRaises(Exception, target.build)
        cleanup_func_mock.assert_called_once()
"""

"""
class MockBuildTargetLoader(BuildTargetLoader):

    def __init__(self, build_targets: Dict[str, BuildTarget]):
        super().__init__()
        self.build_targets = build_targets

    def get_build_target(self, name: str):
        return self.build_targets.get(name)

    def get_all_targets(self):
        return self.build_targets.values()


class TestBuilderFunctions(unittest.TestCase):

    TARGET_NAME_BASE = ["createdirs", "downloadfiles", "convertfiles", "runtilemaker"]
    LOADED_TARGET_BASE: Dict[str, BuildTarget] = {
            "createdirs": BuildTarget(name="createdirs", build=lambda: None),
            "downloadfiles": BuildTarget(name="downloadfiles", build=lambda: None),
            "convertfiles": BuildTarget(name="convertfiles", build=lambda: None)
    }

    # def test_no_duplicate_targets_allowed(self):
    #     target_names = TestBuilder.TARGET_NAME_BASE + ["convertfiles"]
    #
    #     self.assertRaises(BuildException, Builder( MockBuildTargetLoader({}), [])._get_and_verify_targets_to_run, target_names)

    def test_iterate_targets_raises_circular_dependencies_exc(self):

    def test_top_level_target_existence_check(self):
        tree = Builder(MockBuildTargetLoader(TestBuilder.LOADED_TARGET_BASE), [])

        self.assertRaises(BuildException, tree._get_and_verify_targets_to_run, TestBuilder.TARGET_NAME_BASE)

    def test_circular_dependency_check(self):
        loaded_targets = TestBuilder.LOADED_TARGET_BASE.copy()
        loaded_targets["createdirs"]._dependency_names = ["downloadfiles", "convertfiles"]
        loaded_targets["downloadfiles"]._dependency_names = ["createdirs"]

        self.assertRaises(BuildException, Builder, MockBuildTargetLoader(loaded_targets), ["createdirs"])

    def test_get_targets_succeeds(self):
        loader_mock = MockBuildTargetLoader(TestBuilder.LOADED_TARGET_BASE)
        # we'll just collect all build target names our loader knows about
        target_names = [bt.name for name, bt in TestBuilder.LOADED_TARGET_BASE.items()]
        expected_target_list = [bt for name, bt in TestBuilder.LOADED_TARGET_BASE.items()]

        targets_loaded = Builder(loader_mock, [])._get_and_verify_targets_to_run(target_names)
        self.assertListEqual(expected_target_list, targets_loaded)

    def test_dependency_target_does_not_exist(self):
        loaded_targets = TestBuilder.LOADED_TARGET_BASE.copy()
        loaded_targets["createdirs"]._dependency_names = ["downloadfiles", "convertfiles"]
        del loaded_targets["convertfiles"]

        self.assertRaises(BuildException, Builder, MockBuildTargetLoader(loaded_targets), ["createdirs"])

    def test_load_build_success(self):
        loaded_targets = TestBuilder.LOADED_TARGET_BASE.copy()
        loaded_targets["createdirs"]._dependency_names = ["downloadfiles", "convertfiles"]
        loaded_targets["downloadfiles"]._dependency_names = ["convertfiles"]

        tree = None
        try:
            tree = Builder( MockBuildTargetLoader(loaded_targets), ["createdirs"])
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

        builder = Builder(target_loader=mock_target_loader, targets_to_run=["one", "two", "three"])
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

        builder = Builder(target_loader=mock_target_loader, targets_to_run=["one", "two", "three"])
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

        builder = Builder(target_loader=mock_target_loader, targets_to_run=["one", "two", "three"])
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

        builder = Builder(target_loader=mock_target_loader, targets_to_run=["one", "two", "three"])
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
            "one": BuildTarget(build=mock.build_func_one, name="one", dependencies=["two", "three"]),
            "two": BuildTarget(build=mock.build_func_two, name="two"),
            "three": BuildTarget(build=mock.build_func_three, name="three", dependencies=["four"]),
            "four": BuildTarget(build=mock.build_func_four, name="four"),
            "five": BuildTarget(build=mock.build_func_five, name="five"),
            "six": BuildTarget(build=mock.build_func_six, name="six")
        }

        mock_target_loader = MockBuildTargetLoader(BUILD_TARGETS)

        builder = Builder(target_loader=mock_target_loader, targets_to_run=["one", "five"])
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

    def test_cleanup_runs_in_the_correct_order(self):
        mock = MagicMock()

        mock.clean_func_one.return_value = None
        mock.clean_func_two.return_value = None
        mock.clean_func_three.return_value = None
        mock.clean_func_four.return_value = None
        mock.clean_func_five.return_value = None
        mock.clean_func_six.return_value = None

        BUILD_TARGETS = {
            "one": BuildTarget(build=lambda: None, cleanup=mock.clean_func_one, name="one", dependencies=["two", "three"]),
            "two": BuildTarget(build=lambda: None, cleanup=mock.clean_func_two, name="two"),
            "three": BuildTarget(build=lambda: None, cleanup=mock.clean_func_three, name="three", dependencies=["four", "two"]),
            "four": BuildTarget(build=lambda: None, cleanup=mock.clean_func_four, name="four", dependencies=["two"]),
            "five": BuildTarget(build=lambda: None, cleanup=mock.clean_func_five, name="five", dependencies=["three"]),
            "six": BuildTarget(build=lambda: None, cleanup=mock.clean_func_six, name="six")
        }

        mock_target_loader = MockBuildTargetLoader(BUILD_TARGETS)

        builder = Builder(target_loader=mock_target_loader, targets_to_run=["one", "five"])
        builder.clean()

        expected_calls = [
            call.clean_func_five(),
            call.clean_func_three(),
            call.clean_func_two(),
            call.clean_func_four(),
            call.clean_func_two(),
            call.clean_func_one(),
            call.clean_func_three(),
            call.clean_func_two(),
            call.clean_func_four(),
            call.clean_func_two(),
            call.clean_func_two()
        ]

        mock.assert_has_calls(calls=expected_calls, any_order=False)
        mock.clean_func_six.assert_not_called()

    def test_dry_run_does_not_run_build_functions(self):
        mock = MagicMock()

        mock.build_func_one.return_value = None
        mock.build_func_two.return_value = None
        mock.build_func_three.return_value = None
        mock.build_func_four.return_value = None
        mock.build_func_five.return_value = None

        BUILD_TARGETS = {
            "one": BuildTarget(build=mock.build_func_one, name="one", dependencies=["two", "three"]),
            "two": BuildTarget(build=mock.build_func_two, name="two"),
            "three": BuildTarget(build=mock.build_func_three, name="three", dependencies=["four"]),
            "four": BuildTarget(build=mock.build_func_four, name="four"),
            "five": BuildTarget(build=mock.build_func_five, name="five")
        }

        mock_target_loader = MockBuildTargetLoader(BUILD_TARGETS)

        builder = Builder(target_loader=mock_target_loader, targets_to_run=["one", "five"])
        builder.dry_run()

        mock.build_func_one.assert_not_called()
        mock.build_func_two.assert_not_called()
        mock.build_func_three.assert_not_called()
        mock.build_func_four.assert_not_called()
        mock.build_func_five.assert_not_called()

    def test_list_targets_returns_strings(self):
        mock = MagicMock()

        mock.build_func_one.return_value = None
        mock.build_func_two.return_value = None
        mock.build_func_three.return_value = None
        mock.build_func_four.return_value = None
        mock.build_func_five.return_value = None

        BUILD_TARGETS = {
            "one": BuildTarget(build=mock.build_func_one, name="one", dependencies=["two", "three"]),
            "two": BuildTarget(build=mock.build_func_two, name="two"),
            "three": BuildTarget(build=mock.build_func_three, name="three", dependencies=["four"]),
            "four": BuildTarget(build=mock.build_func_four, name="four"),
            "five": BuildTarget(build=mock.build_func_five, name="five")
        }

        mock_target_loader = MockBuildTargetLoader(BUILD_TARGETS)

        builder = Builder(target_loader=mock_target_loader, targets_to_run=["one", "five"])
        non_verbose = builder.list_targets()
        verbose = builder.list_targets(verbose=True)

        # non-verbose and verbose produce something
        self.assertIsNotNone(non_verbose)
        self.assertIsNotNone(verbose)

        # verbose produces more than non-verbose
        self.assertGreater(len(verbose), len(non_verbose))

    def test_handle(self):
        pass
"""
if __name__ == '__main__':
    unittest.main()
