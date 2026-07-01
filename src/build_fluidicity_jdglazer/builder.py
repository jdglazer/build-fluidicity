from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional

from build_fluidicity_jdglazer.exceptions import BuildException
from build_fluidicity_jdglazer.loaders import BuildTargetLoader
from build_fluidicity_jdglazer.targets import BuildTarget


class Builder:

     def __init__(self, targets_to_run: List[str], target_loader: BuildTargetLoader, verbose: bool = False):
         self._verbose = verbose

         self._target_loader = target_loader
         
         self._verify_targets_to_run(targets_to_run)
             
         self._targets_to_run = [self._target_loader.get_build_target(t_name) for t_name in targets_to_run]

         self._verify_targets_exist_and_no_circular_dependencies()

     def _verify_targets_to_run(self, targets_to_run: List[str]) -> None:
         if len(targets_to_run) != len(set(targets_to_run)):
             raise BuildException(f"Duplicate targets found in list of targets to run")

         for target_name in targets_to_run:
             target = self._target_loader.get_build_target(target_name)

             if target is None:
                 raise BuildException(f"Could not find target named '{target_name}'")

     def _verify_targets_exist_and_no_circular_dependencies(self) -> None:
         for target in self._targets_to_run:
             self._iterate_dependency_tree(target)

     def _iterate_dependency_tree(self, initial_target: BuildTarget, target_post_handler: Optional[Callable[[BuildTarget], None]] = None, target_pre_handler: Optional[Callable[[BuildTarget], None]] = None, reverse_dependency_processing=False) -> None:
         dep_name_stack: List[str] = []

         def i(build_target: BuildTarget):
             current_build_target_name = build_target._name

             if current_build_target_name in dep_name_stack:
                 dep_path_desc = " -> ".join(dep_name_stack + [current_build_target_name])
                 raise BuildException("Circular dependency condition found: " + dep_path_desc)

             dep_name_stack.append(build_target.name)

             if callable(target_pre_handler):
                 target_pre_handler(build_target)

             if build_target.dependency_names is not None:
                 dep_names = reversed(build_target.dependency_names) if reverse_dependency_processing else build_target.dependency_names
                 for dep_name in dep_names:
                     target = self._target_loader.get_build_target(dep_name)

                     if target is None:
                         raise BuildException(f"Could not find target named '{dep_name}'")
                     i(target)

             if callable(target_post_handler):
                 target_post_handler(build_target)

             dep_name_stack.pop()

         # entry point into iterative logic
         i(initial_target)

     def run(self) -> None:

         targets_run: List[BuildTarget] = []

         def run_target(target_to_run: BuildTarget):
             if self._verbose:
                 print(f"Running target '{target_to_run.name}'...")

             # we let exceptions propagate out from build to stop the recursive build iteration
             if target_to_run.build():
                 targets_run.append(target_to_run)

         try:
             for target in self._targets_to_run:
                 self._iterate_dependency_tree(target, target_post_handler=run_target)
         except:
             # Attempt to run cleanup in the reverse order we ran the build
             for target in reversed(targets_run):
                 if self._verbose:
                     print(f"Running cleanup for target {target.name}")
                 target.cleanup()

     def clean(self) -> None:
         def clean_target(target_to_clean: BuildTarget) -> None:
             if self._verbose:
                 print(f"Running cleanup for target '{target_to_clean.name}'")

             target_to_clean.cleanup()

         for target in reversed(self._targets_to_run):
             self._iterate_dependency_tree(target, target_pre_handler=clean_target, reverse_dependency_processing=True)