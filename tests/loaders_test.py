import unittest
from unittest.mock import MagicMock

from build_fluidicity_jdglazer.exceptions import UnknownTargetException
from build_fluidicity_jdglazer.loaders import BasicBuildTargetLoader
from test_utils import UltraSimpleBuildTargetSub


class TestBasicBuildTargetLoader(unittest.TestCase):

    def test_no_build_targets(self):
        loader = BasicBuildTargetLoader()
        self.assertEqual(len(list(loader.get_all_targets())), 0)

    def test_build_target_returned_by_name(self):
        loader = BasicBuildTargetLoader()
        target = UltraSimpleBuildTargetSub(name="test_name")
        loader.add_target(target)
        self.assertEqual(target, loader.get_build_target("test_name"))

    def test_all_build_targets_returned(self):
        loader = BasicBuildTargetLoader()

        target1 = UltraSimpleBuildTargetSub(name="test_name_1")
        loader.add_target(target1)

        target2 = UltraSimpleBuildTargetSub(name="test_name_2")
        loader.add_target(target2)

        self.assertListEqual([target1, target2], list(loader.get_all_targets()))

    def test_unknown_target_exception(self):
        loader = BasicBuildTargetLoader()
        self.assertRaises(UnknownTargetException, loader.get_build_target, "does_not_exist")

    def test_list_target_writes_succinctly(self):
        loader = BasicBuildTargetLoader()
        name1 = "test_name_1"
        desc1 = "test name 1 description"
        name2 = "test_name_2"
        desc2 = "test name 2 description"
        loader.add_target(UltraSimpleBuildTargetSub(name=name1, description=desc1))
        loader.add_target(UltraSimpleBuildTargetSub(name=name2, description=desc2))

        mock = MagicMock()
        loader.list_targets(verbose=False, write_to=mock)
        s = ""

        for call in mock.call_args_list:
            s += call[0][0]

        self.assertTrue(s.find(name1) >= 0)
        self.assertTrue(s.find(name2) >= 0)
        self.assertTrue(s.find(desc1) < 0)
        self.assertTrue(s.find(desc2) < 0)

    def test_list_target_writes_verbosely(self):
        loader = BasicBuildTargetLoader()
        name1 = "test_name_1"
        desc1 = "test name 1 description"
        name2 = "test_name_2"
        desc2 = "test name 2 description"
        loader.add_target(UltraSimpleBuildTargetSub(name=name1, description=desc1))
        loader.add_target(UltraSimpleBuildTargetSub(name=name2, description=desc2))

        mock = MagicMock()
        loader.list_targets(verbose=True, write_to=mock)
        s = ""

        for call in mock.call_args_list:
            s += call[0][0]

        self.assertTrue(s.find(name1) >= 0)
        self.assertTrue(s.find(name2) >= 0)
        self.assertTrue(s.find(desc1) >= 0)
        self.assertTrue(s.find(desc2) >= 0)