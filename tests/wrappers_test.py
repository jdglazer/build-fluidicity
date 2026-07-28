#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
import unittest
from unittest.mock import MagicMock, patch

from build_fluidicity.wrappers import LoggingBuildTargetBaseWrapper
from build_fluidicity.exceptions import BuildException
from build_fluidicity.targets import TargetLifecycle


class TestLoggingBuildTargetBaseWrapper(unittest.TestCase):

    def setUp(self):
        target = MagicMock()
        target.do_build = MagicMock()
        target.do_build.return_value = True
        target.do_cleanup = MagicMock()
        target.do_completion_test = MagicMock()
        target.do_completion_test.return_value = False
        self.target = target

        self.wrapper = LoggingBuildTargetBaseWrapper(target)

    def test_expected_super_type_present(self):
        self.assertIsInstance(self.wrapper, TargetLifecycle)

    def test_wrapped_functions_called_and_returns_propagated(self):

        self.assertTrue(self.wrapper.do_build())
        self.assertFalse(self.wrapper.do_completion_test())
        self.wrapper.do_cleanup()

        self.target.do_build.assert_called_once()
        self.target.do_completion_test.assert_called_once()
        self.target.do_cleanup.assert_called_once()

    @patch('build_fluidicity.wrappers.log')
    def test_log_called_for_each(self, log_mock):
        self.wrapper.do_build()
        log_mock.assert_called_once()
        log_mock.reset_mock()

        self.wrapper.do_completion_test()
        log_mock.assert_called_once()
        log_mock.reset_mock()

        self.wrapper.do_cleanup()
        log_mock.assert_called_once()
        log_mock.reset_mock()

    @patch('build_fluidicity.wrappers.log_exception')
    def test_log_exception_called(self, log_exception_mock):
        self.target.do_build.side_effect = BuildException("")
        self.assertRaises(BuildException, self.wrapper.do_build)
        log_exception_mock.assert_called_once()
        log_exception_mock.reset_mock()

        self.target.do_completion_test.side_effect = BuildException("")
        self.assertRaises(BuildException, self.wrapper.do_completion_test)

        self.target.do_cleanup.side_effect = BuildException("")
        self.assertRaises(BuildException, self.wrapper.do_cleanup)
        log_exception_mock.assert_called_once()
        log_exception_mock.reset_mock()