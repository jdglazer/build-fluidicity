import unittest

from build_fluidicity_jdglazer.loaders import BasicBuildTargetLoader
from build_fluidicity_jdglazer.targets import BuildTarget


class TestBasicBuildTargetLoader(unittest.TestCase):

     def test_no_build_targets(self):
         loader = BasicBuildTargetLoader()
         self.assertEqual(len(list(loader.get_all_targets())), 0)

     def test_build_target_returned_by_name(self):
         loader = BasicBuildTargetLoader()
         target = BuildTarget(name="test_name", build=lambda: None)
         loader.add_target(target)
         self.assertEqual(target, loader.get_build_target("test_name"))

     def test_all_build_targets_returned(self):
         loader = BasicBuildTargetLoader()

         target1 = BuildTarget(name="test_name_1", build=lambda: None)
         loader.add_target(target1)

         target2 = BuildTarget(name="test_name_2", build=lambda: None)
         loader.add_target(target2)

         self.assertListEqual([target1, target2], list(loader.get_all_targets()))