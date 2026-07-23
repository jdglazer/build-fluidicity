import unittest
from typing import List
from unittest.mock import MagicMock

from build_fluidicity_jdglazer.compilers import Compiler
from build_fluidicity_jdglazer.exceptions import BuildException, CircularDependencyException, UnknownTargetException
from build_fluidicity_jdglazer.loaders import build_target_loader, BasicBuildTargetLoader
from test_utils import UltraSimpleBuildTargetSub


class TestCompiler(unittest.TestCase):

    # order for [target_top1, target_top2]:
    # target_lower_1 -> target_middle_2 -> target_lower_1 -> target_middle_1 ->
    # target_lower_1 -> target_middle_2 -> target_top1 -> target_top2
    TARGET_DEPS_DEFAULT = target_deps = {
            "target_top2": [],
            "target_top1": ["target_middle_1", "target_middle_2"],
            "target_middle_1": ["target_middle_2", "target_lower_1"],
            "target_middle_2": ["target_lower_1"],
            "target_lower_1": []
    }

    def __init__(self, h) -> None:
        super().__init__(h)
        self._compiler = Compiler(target_loader=build_target_loader)

    def _get(self, key: str) -> List[str]:
        return TestCompiler.TARGET_DEPS_DEFAULT[key]

    def test_iterate_targets_correct_iteration_count(self):
        iterations = 0
        for a in self._compiler._iterate_targets(["target_top1", "target_top2"], self._get):
            iterations += 1

        self.assertEqual(iterations, 8)

    def test_iterate_targets_correct_iteration_order(self):
        names = []
        for name, depth in self._compiler._iterate_targets(["target_top1", "target_top2"], self._get):
            names.append(name)

        expected_names = ["target_lower_1", "target_middle_2",  "target_lower_1", "target_middle_1",
                          "target_lower_1", "target_middle_2", "target_top1", "target_top2" ]

        self.assertSequenceEqual(names, expected_names)

    def test_iterate_targets_propagates_dep_getter_exceptions(self):
        mock = MagicMock()
        mock.side_effect = BuildException("Here i am")
        iterator = self._compiler._iterate_targets(["target_top1", "target_top2"], mock)

        self.assertRaises(BuildException, iterator.__next__)

    def test_iterate_targets_raises_circular_dependency_exception(self):
        t_deps = {
            "one": ["two", "three"],
            "two": ["four"],
            "three": ["two"],
            "four": ["five", "one"],
            "five": []
        }

        def get(s: str) -> List[str]:
            return t_deps[s]

        iterator = self._compiler._iterate_targets(["one"], get)
        # list will iterate through the iterable
        self.assertRaises(CircularDependencyException, list, iterator)

    def _build_loader(self) -> BasicBuildTargetLoader:
        loader = BasicBuildTargetLoader()
        target_top1 = UltraSimpleBuildTargetSub(name="target_top1", dependencies=["target_middle_1", "target_middle_2"])
        loader.add_target(target_top1)

        target_top2 = UltraSimpleBuildTargetSub(name="target_top2", dependencies=[])
        loader.add_target(target_top2)

        target_middle_1 = UltraSimpleBuildTargetSub(name="target_middle_1",
                                                    dependencies=["target_middle_2", "target_lower_1"])
        loader.add_target(target_middle_1)

        target_middle_2 = UltraSimpleBuildTargetSub(name="target_middle_2", dependencies=["target_lower_1"])
        loader.add_target(target_middle_2)

        target_lower_1 = UltraSimpleBuildTargetSub(name="target_lower_1", dependencies=[])
        loader.add_target(target_lower_1)

        return loader

    def test_compile_exception_when_target_is_missing_from_loader(self):
        loader = self._build_loader()

        del loader._build_targets["target_lower_1"]

        compiler = Compiler(loader)
        self.assertRaises(UnknownTargetException, compiler.compile, ["target_top2", "target_top1"])

    def test_compile_success(self):
        loader = self._build_loader()

        compiler = Compiler(loader)

        compiler.compile(["target_top2", "target_top1"])

        expected_values = [(loader.get_build_target("target_top2"), 1),
                           (loader.get_build_target("target_lower_1"), 4),
                           (loader.get_build_target("target_middle_2"), 3),
                           (loader.get_build_target("target_lower_1"), 3),
                           (loader.get_build_target("target_middle_1"), 2),
                           (loader.get_build_target("target_lower_1"), 3),
                           (loader.get_build_target("target_middle_2"), 2),
                           (loader.get_build_target("target_top1"), 1)]

        self.assertSequenceEqual(compiler.result(), expected_values)

    def test_show_target_heirarchy(self):
        loader = self._build_loader()
        compiler = Compiler(loader)
        compiler.compile(["target_top2", "target_top1"])
        mock = MagicMock()

        compiler.show_target_hierarchy(verbose = True, write_to=mock)
        s = ""
        for call in mock.call_args_list:
            s += call[0][0]

        self.assertTrue(s.find("*target_top2") >= 0)
        self.assertTrue(s.find("|||*target_lower_1") >= 0)
        self.assertTrue(s.find("||*target_lower_1") >= 0)
        self.assertTrue(s.find("||*target_middle_2") >= 0)
        self.assertTrue(s.find("|*target_middle_2") >= 0)
        self.assertTrue(s.find("|*target_middle_1") >= 0)
        self.assertTrue(s.find("*target_top1") >= 0)


if __name__ == '__main__':
    unittest.main()