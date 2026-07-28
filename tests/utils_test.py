#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
import unittest
from typing import List
from unittest.mock import MagicMock, patch

from build_fluidicity.exceptions import BuildException, CircularDependencyException
from build_fluidicity.utils import iterate_items, log_exception


class TestUtilsMethods(unittest.TestCase):

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

    @staticmethod
    def _get(key: str) -> List[str]:
        return TestUtilsMethods.TARGET_DEPS_DEFAULT[key]

    def test_iterate_items_correct_iteration_count(self):
        iterations = len(list(iterate_items(["target_top1", "target_top2"], self._get)))

        self.assertEqual(iterations, 8)

    def test_iterate_targets_correct_iteration_order(self):
        names = []
        for name, depth in iterate_items(["target_top1", "target_top2"], self._get):
            names.append(name)

        expected_names = ["target_lower_1", "target_middle_2",  "target_lower_1", "target_middle_1",
                          "target_lower_1", "target_middle_2", "target_top1", "target_top2" ]

        self.assertSequenceEqual(names, expected_names)

    def test_iterate_targets_propagates_dep_getter_exceptions(self):
        mock = MagicMock()
        mock.side_effect = BuildException("Here i am")
        iterator = iterate_items(["target_top1", "target_top2"], mock)

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

        iterator = iterate_items(["one"], get)
        # list will iterate through the iterable
        self.assertRaises(CircularDependencyException, list, iterator)

    @patch('build_fluidicity.utils.print')
    def test_log_exception(self, print_mock):
        try:
            raise BuildException("Here i am")
        except BuildException:
            log_exception("Test")

        print_mock.assert_called()

if __name__ == '__main__':
    unittest.main()
