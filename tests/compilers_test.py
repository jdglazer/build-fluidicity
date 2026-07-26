#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
import unittest
from unittest.mock import MagicMock

from build_fluidicity_jdglazer.compilers import CompilerImpl
from build_fluidicity_jdglazer.exceptions import UnknownTargetException
from build_fluidicity_jdglazer.loaders import BasicBuildTargetLoader, build_target_loader
from testingutils import UltraSimpleBuildTargetSub, SimpleClassA, SimpleClassB


class TestCompilerImpl(unittest.TestCase):

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

        compiler = CompilerImpl(loader)
        self.assertRaises(UnknownTargetException, compiler.compile, ["target_top2", "target_top1"])

    def test_compile_success(self):
        loader = self._build_loader()

        compiler = CompilerImpl(loader)

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
        compiler = CompilerImpl(loader)
        compiler.compile(["target_top2", "target_top1"])
        mock = MagicMock()

        compiler.show_target_hierarchy(verbose = True, write_to=mock)
        s = ""
        for call in mock.call_args_list:
            s += call[0][0]

        self.assertTrue(s.find("*target_top2") >= 0)
        self.assertTrue(s.find("| | | *target_lower_1") >= 0)
        self.assertTrue(s.find("| | *target_lower_1") >= 0)
        self.assertTrue(s.find("| | *target_middle_2") >= 0)
        self.assertTrue(s.find("| *target_middle_2") >= 0)
        self.assertTrue(s.find("| *target_middle_1") >= 0)
        self.assertTrue(s.find("*target_top1") >= 0)

    def test_wrap_build_target_no_wrappers_returns_original_target(self):
        compiler = CompilerImpl(build_target_loader, target_wrappers=None)
        target = UltraSimpleBuildTargetSub(name="target")
        self.assertIsInstance(compiler._wrap_build_target(target), UltraSimpleBuildTargetSub)

    def test_wrap_build_target_correct_wrap_order(self):

        compiler = CompilerImpl(build_target_loader, target_wrappers = [SimpleClassA, SimpleClassB])

        wrapped_obj = compiler._wrap_build_target(UltraSimpleBuildTargetSub(name="target"))

        self.assertIsInstance(wrapped_obj, SimpleClassB)
        self.assertIsInstance(wrapped_obj._wrapped_target, SimpleClassA)
        self.assertIsInstance(wrapped_obj._wrapped_target._wrapped_target, UltraSimpleBuildTargetSub)


if __name__ == '__main__':
    unittest.main()