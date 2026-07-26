#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
import argparse
from typing import Optional, List

from build_fluidicity_jdglazer.builder import BuilderImpl
from build_fluidicity_jdglazer.compilers import CompilerImpl
from build_fluidicity_jdglazer.exceptions import UnknownTargetException
from build_fluidicity_jdglazer.loaders import BuildTargetLoader
from build_fluidicity_jdglazer.utils import log_exception
from build_fluidicity_jdglazer.wrappers import LoggingBuildTargetBaseWrapper


def _handle_list(build_target_loader: BuildTargetLoader, verbose: bool, target_name: Optional[str] = None) -> None:
    """Handles -list command and relevant options
    Args:
        build_target_loader: the loader with all build targets
        verbose: if True, add extra details to output if true
        target_name: The name of the target for which to list information, if omitted all targets will be listed

    Returns: None
    """
    if target_name is None:
        build_target_loader.list_targets(verbose=verbose)
    else:
        try:
            target = build_target_loader.get_build_target(target_name)
            print(target)
        except UnknownTargetException:
            print(f"Target '{target_name}' not found")


def _handle_run(build_target_loader: BuildTargetLoader, verbose: bool, dry: bool, target_names: List[str]) -> None:
    """Handles -run command and relevant options

    Args:
        build_target_loader: the loader with all build targets
        verbose: if True, add logging output or extra details if dry is True
        dry: if True, run show build target run order
        target_names: Targets to run

    Returns: None
    """
    if len(target_names) == 0:
        return

    target_wrappers = [LoggingBuildTargetBaseWrapper] if verbose else None
    _compiler = CompilerImpl(build_target_loader, target_wrappers = target_wrappers)

    _compiler.compile(target_names)
    if dry:
        _compiler.show_target_hierarchy(verbose=verbose)
    else:
        BuilderImpl(_compiler).run()


def _handle_clean(build_target_loader: BuildTargetLoader, verbose: bool, clean_targets: List[str]) -> None:
    """Handles -clean command and relevant options

    Args:
        build_target_loader: the loader with all build targets
        verbose: if True, add logging output
        clean_targets: Targets to clean

    Returns: None
    """
    if clean_targets == 0:
        return

    target_wrappers = [LoggingBuildTargetBaseWrapper] if verbose else None
    _compiler = CompilerImpl(build_target_loader, target_wrappers = target_wrappers)
    _compiler.compile(clean_targets)
    BuilderImpl(_compiler).clean()


_DRY_FLAG = "--dry"
_VERBOSE_FLAG = "--verbose"

_LIST_ARG = "-list"
_RUN_ARG = "-run"
_CLEAN_ARG = "-clean"

def handle_args(build_target_loader: BuildTargetLoader, args_in: Optional[List[str]] = None) -> None:
    """Primary entry point to command line application

    Args:
        build_target_loader: the loader with all build targets
        args_in: We can override the default sys.argv input by provided a list of args here (mainly for testing)

    Returns: None
    """
    assert isinstance(build_target_loader, BuildTargetLoader), "Invalid argument type"
    arg_parser = argparse.ArgumentParser(description="Build Fluidicity commandline application")

    main_group = arg_parser.add_mutually_exclusive_group(required=True)

    main_group.add_argument(_LIST_ARG,
                            nargs='?',
                            default=None,
                            action="append",
                            metavar="target name",
                            help="List build targets. If no argument is provided, lists all available build targets")
    main_group.add_argument(_RUN_ARG,
                            nargs='*',
                            action="store",
                            metavar="target name",
                            help="Run build targets specified by name")
    main_group.add_argument(_CLEAN_ARG,
                            nargs='*',
                            action="store",
                            metavar="target name",
                            help="Run clean on targets specified by name")

    arg_parser.add_argument(_DRY_FLAG,
                            action="store_true",
                            default=False,
                            help="Iterate through build steps without running. This will print information on build steps")
    arg_parser.add_argument(_VERBOSE_FLAG,
                            action="store_true",
                            default=False,
                            help="List or log more details")

    args = arg_parser.parse_args(args=args_in)

    try:
        if args.list is not None:
            _handle_list(build_target_loader, args.verbose, args.list[0])
        elif args.run is not None:
            _handle_run(build_target_loader, args.verbose, args.dry, list(args.run))
        elif args.clean is not None:
            _handle_clean(build_target_loader, args.verbose, list(args.clean))
    except Exception:
        log_exception("Error")
