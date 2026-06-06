import sys
import unittest
from typing import Dict, override

sys.path.append('.\\src')

from build_fluidicity.builder import BuildTargetLoader, BuildTree, BuildException, BuildTarget

class MockBuildTargetLoader(BuildTargetLoader):

    def __init__(self, build_targets: Dict[str, BuildTarget]):
        self.build_targets = build_targets

    @override
    def load_available_build_targets(self):
        return self.build_targets

class TestBuildTree(unittest.TestCase):

    TARGET_NAME_BASE = ["createdirs", "downloadfiles", "convertfiles", "runtilemaker"]
    LOADED_TARGET_BASE: Dict[str, BuildTarget] = {
            "createdirs": BuildTarget(name="createdirs", build=lambda: None),
            "downloadfiles": BuildTarget(name="downloadfiles", build=lambda: None),
            "convertfiles": BuildTarget(name="convertfiles", build=lambda: None)
    }

    def test_no_duplicate_targets_allowed(self):
        target_names = TestBuildTree.TARGET_NAME_BASE + ["convertfiles"]

        self.assertRaises(BuildException, BuildTree([], MockBuildTargetLoader({}))._verify_targets_to_run, target_names)

    def test_top_level_target_existence_check(self):
        tree = BuildTree([], MockBuildTargetLoader(TestBuildTree.LOADED_TARGET_BASE))

        self.assertRaises(BuildException, tree._verify_targets_to_run, TestBuildTree.TARGET_NAME_BASE)

    def test_circular_dependency_check(self):
        loaded_targets = TestBuildTree.LOADED_TARGET_BASE.copy()
        loaded_targets["createdirs"].dependency_names = ["downloadfiles", "convertfiles"]
        loaded_targets["downloadfiles"].dependency_names = ["createdirs"]

        self.assertRaises(BuildException, BuildTree, ["createdirs"], MockBuildTargetLoader(loaded_targets))

    def test_dependency_target_does_not_exist_check(self):
        loaded_targets = TestBuildTree.LOADED_TARGET_BASE.copy()
        loaded_targets["createdirs"].dependency_names = ["downloadfiles", "convertfiles"]
        del loaded_targets["convertfiles"]

        self.assertRaises(BuildException, BuildTree, ["createdirs"], MockBuildTargetLoader(loaded_targets))

    def test_load_build_success(self):
        loaded_targets = TestBuildTree.LOADED_TARGET_BASE.copy()
        loaded_targets["createdirs"].dependency_names = ["downloadfiles", "convertfiles"]
        loaded_targets["downloadfiles"].dependency_names = ["convertfiles"]

        tree = None
        try:
            tree = BuildTree(["createdirs"], MockBuildTargetLoader(loaded_targets))
        except:
            pass

        self.assertIsNotNone(tree)

if __name__ == '__main__':
    unittest.main()
