import argparse

from typing import List, Iterable

from build_fluidicity_jdglazer.compilers import BaseCompiler, Compiler
from build_fluidicity_jdglazer.loaders import BuildTargetLoader
from build_fluidicity_jdglazer.targets import TargetLifecycle


class Builder:

    def __init__(self, compiler: BaseCompiler) -> None:
        self._compiler = compiler

    def _build_target(self, target: TargetLifecycle) -> bool:
        """
        Runs the build function if completion test is not set or returns false

        :return: True if the build function was run, false otherwise
        """
        if target.do_completion_test():
            return False

        try:
            return target.do_build()
        except Exception as e:
            target.do_cleanup()
            raise e

    def _clean_targets(self, targets: Iterable[TargetLifecycle]) -> None:
        for target in targets:
            try:
                target.do_cleanup()
            except:
                pass

    def run(self) -> None:

        targets_run: List[TargetLifecycle] = []

        for target, depth in self._compiler.result():

            try:
                if self._build_target(target):
                    targets_run.append(target)
            except:
                self._clean_targets(reversed(targets_run))

    def clean(self) -> None:
        for target, depth in reversed(self._compiler.result()):
            try:
                target.do_cleanup()
            except:
                pass


def handle_args(build_target_loader: BuildTargetLoader) -> None:
    arg_parser = argparse.ArgumentParser(description="Build Fluidicity commandline application")

    main_group = arg_parser.add_mutually_exclusive_group(required=True)

    main_group.add_argument("-list",
                            nargs='?',
                            action="append",
                            metavar="target name",
                            help="List build targets. If no argument is provided, lists all available build targets")
    main_group.add_argument("-run",
                            nargs='*',
                            action="store",
                            metavar="target name",
                            help="Run build targets specified by name")
    main_group.add_argument("-clean",
                            nargs='*',
                            action="store",
                            metavar="target name",
                            help="Run clean on targets specified by name")

    arg_parser.add_argument("--dry",
                            action="store_true",
                            default=False,
                            help="Iterate through build steps without running. This will print information on build steps")
    arg_parser.add_argument("--verbose",
                            action="store_true",
                            default=False,
                            help="List or log more details")

    args = arg_parser.parse_args()

    _compiler = Compiler(build_target_loader)
    _builder = Builder(_compiler)

    try:
        if args.list is not None:
            if args.list[0] is None:
                build_target_loader.list_targets(verbose = args.verbose)
            else:
                target_name = args.list[0]

                target = build_target_loader.get_build_target(target_name)
                if target is None:
                    print(f"Target '{target_name}' not found")
                else:
                    print(target)
        elif args.run is not None:
            if len(args.run) == 0:
                return

            args_to_run = list(args.run)
            _compiler.compile(args_to_run)
            if args.dry:
                _compiler.show_target_hierarchy(verbose = args.verbose)
            else:
                _builder.run()
        elif args.clean is not None:
            if len(args.clean) == 0:
                return

            args_to_run = list(args.clean)
            _compiler.compile(args_to_run)
            _builder.clean()
    except Exception as e:
        print("Error: " + str(e))