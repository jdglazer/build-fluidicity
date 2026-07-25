#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
import unittest
from unittest.mock import MagicMock, patch

from build_fluidicity_jdglazer.builder import BuilderImpl
from build_fluidicity_jdglazer.cli import _handle_list, _handle_run, _handle_clean, _LIST_ARG, handle_args, \
    _VERBOSE_FLAG, _RUN_ARG, _DRY_FLAG, _CLEAN_ARG
from build_fluidicity_jdglazer.compilers import CompilerImpl
from build_fluidicity_jdglazer.exceptions import UnknownTargetException, BuildException
from build_fluidicity_jdglazer.loaders import BuildTargetLoader
from build_fluidicity_jdglazer.wrappers import LoggingBuildTargetBaseWrapper
from testingutils import UltraSimpleBuildTargetSub


class TestHandleArgs(unittest.TestCase):

    def setUp(self):
        self.build_target_loader = MagicMock(spec=BuildTargetLoader)

    def test_handle_list_no_args(self):
        _handle_list(self.build_target_loader, verbose = True, target_name = None)

        self.build_target_loader.list_targets.assert_called_with(verbose=True)

    def test_handle_list_with_args(self):
        self.build_target_loader.get_build_target.return_value = UltraSimpleBuildTargetSub(name="target_exists")

        _handle_list(self.build_target_loader, verbose=True, target_name="target_exists")
        self.build_target_loader.get_build_target.assert_called_with("target_exists")

    def test_handle_list_unknown_target_no_exception_propagation(self):
        self.build_target_loader.get_build_target.side_effect = UnknownTargetException("")

        try:
            _handle_list(self.build_target_loader, verbose=True, target_name = "target_exists")
            self.build_target_loader.get_build_target.assert_called_once()
        except UnknownTargetException:
            self.fail("Unexpected exception raised")

    @patch('build_fluidicity_jdglazer.cli.CompilerImpl')
    @patch('build_fluidicity_jdglazer.cli.BuilderImpl')
    def test_handle_run_dry_verbose_run(self, builder_impl_mock, compiler_impl_mock):
        builder_impl_mock.return_value = (builder_instance := MagicMock(spec=BuilderImpl))
        compiler_impl_mock.return_value = (compiler_instance := MagicMock(spec=CompilerImpl))

        _handle_run(self.build_target_loader, verbose = True, dry = True, target_names = ["target_exists"])

        compiler_impl_mock.assert_called_with(self.build_target_loader, target_wrappers=[LoggingBuildTargetBaseWrapper])
        compiler_instance.compile.assert_called_with(["target_exists"])
        compiler_instance.show_target_hierarchy.assert_called_with(verbose=True)
        builder_instance.assert_not_called()

    @patch('build_fluidicity_jdglazer.cli.CompilerImpl')
    @patch('build_fluidicity_jdglazer.cli.BuilderImpl')
    def test_handle_run_live_run(self, builder_impl_mock, compiler_impl_mock):
        builder_impl_mock.return_value = (builder_instance := MagicMock(spec=BuilderImpl))
        compiler_impl_mock.return_value = (compiler_instance := MagicMock(spec=CompilerImpl))

        _handle_run(self.build_target_loader, verbose=True, dry=False, target_names=["target_exists"])

        compiler_instance.compile.assert_called_with(["target_exists"])
        compiler_instance.show_target_hierarchy.assert_not_called()
        builder_impl_mock.assert_called_with(compiler_instance)
        builder_instance.run.assert_called_once()

    @patch('build_fluidicity_jdglazer.cli.CompilerImpl')
    @patch('build_fluidicity_jdglazer.cli.BuilderImpl')
    def test_clean_run(self, builder_impl_mock, compiler_impl_mock):
        builder_impl_mock.return_value = (builder_instance := MagicMock(spec=BuilderImpl))
        compiler_impl_mock.return_value = (compiler_instance := MagicMock(spec=CompilerImpl))

        _handle_clean(self.build_target_loader, False,["target_exists"])
        compiler_instance.compile.assert_called_with(["target_exists"])
        builder_impl_mock.assert_called_with(compiler_instance)
        builder_instance.run.assert_not_called()
        builder_instance.clean.assert_called_once()

    @patch('build_fluidicity_jdglazer.cli._handle_list')
    @patch('build_fluidicity_jdglazer.cli._handle_run')
    @patch('build_fluidicity_jdglazer.cli._handle_clean')
    def test_handle_args_list(self, handle_clean_mock, handle_run_mock, handle_list_mock):
        handle_args(self.build_target_loader, args_in = [_LIST_ARG, "target_exists", _VERBOSE_FLAG])

        handle_list_mock.assert_called_with(self.build_target_loader, True, "target_exists")
        handle_clean_mock.assert_not_called()
        handle_run_mock.assert_not_called()

    @patch('build_fluidicity_jdglazer.cli._handle_list')
    @patch('build_fluidicity_jdglazer.cli._handle_run')
    @patch('build_fluidicity_jdglazer.cli._handle_clean')
    def test_handle_args_run_dry(self, handle_clean_mock, handle_run_mock, handle_list_mock):
        handle_args(self.build_target_loader, args_in = [_RUN_ARG, "target_exists", _DRY_FLAG, _VERBOSE_FLAG])

        handle_run_mock.assert_called_with(self.build_target_loader, True, True, ["target_exists"])
        handle_list_mock.assert_not_called()
        handle_clean_mock.assert_not_called()

    @patch('build_fluidicity_jdglazer.cli._handle_list')
    @patch('build_fluidicity_jdglazer.cli._handle_run')
    @patch('build_fluidicity_jdglazer.cli._handle_clean')
    def test_handle_args_live_run(self, handle_clean_mock, handle_run_mock, handle_list_mock):
        handle_args(self.build_target_loader, args_in = [_RUN_ARG, "target_exists"])

        handle_run_mock.assert_called_with(self.build_target_loader, False, False, ["target_exists"])
        handle_list_mock.assert_not_called()
        handle_clean_mock.assert_not_called()

    @patch('build_fluidicity_jdglazer.cli._handle_list')
    @patch('build_fluidicity_jdglazer.cli._handle_run')
    @patch('build_fluidicity_jdglazer.cli._handle_clean')
    def test_handle_args_clean(self, handle_clean_mock, handle_run_mock, handle_list_mock):
        handle_args(self.build_target_loader, args_in = [_CLEAN_ARG, "target_exists"])

        handle_clean_mock.assert_called_with(self.build_target_loader, False, ["target_exists"])
        handle_run_mock.assert_not_called()
        handle_list_mock.assert_not_called()

    @patch('build_fluidicity_jdglazer.cli._handle_list')
    @patch('build_fluidicity_jdglazer.cli.log_exception')
    def test_handle_args_exception_swallowed_and_logged(self, log_exception_mock, handle_list_mock):
        handle_list_mock.side_effect = BuildException("")

        try:
            handle_args(self.build_target_loader, args_in = [_LIST_ARG, "target_exists"])
        except:
            self.fail("Should not have thrown an exception")

        log_exception_mock.assert_called_once()