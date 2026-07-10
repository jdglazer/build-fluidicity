import argparse
from typing import Callable, List, Optional

from build_fluidicity_jdglazer.exceptions import BuildException
from build_fluidicity_jdglazer.loaders import BuildTargetLoader
from build_fluidicity_jdglazer.targets import BuildTarget
from build_fluidicity_jdglazer.utils import initialize_logger, log


class Builder:

    def __init__(self, target_loader: BuildTargetLoader, targets_to_run: Optional[List[str]] = None):
        self._target_loader = target_loader

        self._targets_to_run: List[BuildTarget] = []

        # This will verify all the targets exist
        if targets_to_run:
            self.set_targets_to_build(targets_to_run)

        initialize_logger()

    def _get_and_verify_targets_to_run(self, targets_to_run: List[str]) -> List[BuildTarget]:
        if len(targets_to_run) != len(set(targets_to_run)):
            raise BuildException("Duplicate targets found in list of targets to run")

        build_targets = []

        for target_name in targets_to_run:
            target = self._target_loader.get_build_target(target_name)

            if target is None:
                raise BuildException(f"Could not find target named '{target_name}'")

            build_targets.append(target)

        return build_targets

    def _verify_targets_exist_and_no_circular_dependencies(self) -> None:
        for target in self._targets_to_run:
            self._iterate_dependency_tree(target)

    def _iterate_dependency_tree(self, initial_target: BuildTarget,
                                 target_post_handler: Optional[Callable[[BuildTarget], None]] = None,
                                 target_pre_handler: Optional[Callable[[BuildTarget, int], None]] = None,
                                 reverse_dependency_processing=False) -> None:

        dep_name_stack: List[str] = []

        def i(build_target: BuildTarget, recursion_index):
            current_build_target_name = build_target.name

            if current_build_target_name in dep_name_stack:
                dep_path_desc = " -> ".join(dep_name_stack + [current_build_target_name])
                raise BuildException("Circular dependency condition found: " + dep_path_desc)

            dep_name_stack.append(build_target.name)

            if callable(target_pre_handler):
                target_pre_handler(build_target, recursion_index)

            if build_target.dependency_names is not None:
                dep_names = reversed(
                    build_target.dependency_names) if reverse_dependency_processing else build_target.dependency_names
                for dep_name in dep_names:
                    target = self._target_loader.get_build_target(dep_name)

                    if target is None:
                        raise BuildException(f"Could not find target named '{dep_name}'")
                    i(target, recursion_index+1)

            if callable(target_post_handler):
                target_post_handler(build_target)

            dep_name_stack.pop()

        # entry point into iterative logic
        i(initial_target, 0)

    def set_targets_to_build(self, targets_to_run: List[str]) -> None:

        self._targets_to_run = self._get_and_verify_targets_to_run(targets_to_run)

        self._verify_targets_exist_and_no_circular_dependencies()

    def run(self) -> None:

        targets_run: List[BuildTarget] = []

        def run_target(target_to_run: BuildTarget) -> None:
            log(f"Running target '{target_to_run.name}'", target_to_run.name)

            try:
                # we let exceptions propagate out from build to stop the recursive build iteration
                if target_to_run.build():
                    targets_run.append(target_to_run)
            except Exception as e:
                raise BuildException(str(e), original=e, target=target_to_run)

        try:
            for target in self._targets_to_run:
                self._iterate_dependency_tree(target, target_post_handler=run_target)
        except BuildException as be:
            # Attempt to run cleanup in the reverse order we ran the build
            for target in reversed(targets_run):
                log(f"Running cleanup for target '{target.name}'", target.name)
                target.cleanup()

    def dry_run(self) -> None:

        def print_target_hierarchy(build_target: BuildTarget, recursion_index: int) -> None:
            print((" | "*recursion_index)  + " * " + build_target.name)

        def print_target_run_order(build_target: BuildTarget) -> None:
            print(build_target.name)

        print("Target Run Hierarchy")
        print("--------------------")
        for target in self._targets_to_run:
            self._iterate_dependency_tree(target, target_pre_handler=print_target_hierarchy)

        print()
        print("Target Run Order")
        print("----------------")
        for target in self._targets_to_run:
            self._iterate_dependency_tree(target, target_post_handler=print_target_run_order)


    def list_targets(self, verbose = False) -> str:
        if verbose:
            return "\n\r".join(map(lambda x: str(x), self._target_loader.get_all_targets()))

        return "\n\r".join(map(lambda x: x.name, self._target_loader.get_all_targets()))

    def clean(self) -> None:

        def clean_target(target_to_clean: BuildTarget, recursion_index) -> None:
            log(f"Running cleanup for target '{target_to_clean.name}'", target_to_clean.name)
            target_to_clean.cleanup()

        for target in reversed(self._targets_to_run):
            self._iterate_dependency_tree(target, target_pre_handler=clean_target, reverse_dependency_processing=True)

    def handle_args(self) -> None:
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

        try:
            if args.list is not None:
                if args.list[0] is None:
                    print(self.list_targets(args.verbose))
                else:
                    target_name = args.list[0]

                    target = self._target_loader.get_build_target(target_name)
                    if target is None:
                        print(f"Target '{target_name}' not found")
                    else:
                        print(target)
            elif args.run is not None:
                if len(args.run) > 0:
                    self.set_targets_to_build(list(args.run))

                if args.dry:
                    self.dry_run()
                else:
                    self.run()
            elif args.clean is not None:
                if len(args.clean) > 0:
                    self.set_targets_to_build(list(args.clean))
                self.clean()
        except Exception as e:
            print("Error: " + str(e))


