from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional

# static variable to be referenced across project where targets are defined
build_target_loader = BasicBuildTargetLoader()

class BuildException(Exception):

    def __init__(self, message: str = ""):
        self.message = message
        # Forward the message to the parent Exception class
        super().__init__(self.message)

class BuildTarget:

    def __init__(self, name: str, build: Callable[[], None], description: Optional[str] = None, completion_test: Callable[[], bool] = lambda: False, cleanup: Optional[Callable[[], None]] = None, dependency_names: Optional[List[str]] = None):
        self._name = name
        self._do_build = build
        self._description = description
        self._do_completion_test = completion_test
        self._do_cleanup = cleanup
        self._dependency_names = dependency_names

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def dependency_names(self) -> List[str]:
        return self._dependency_names

    def build(self) -> bool:
        """
        Runs the build function if completion test is not set or returns false

        :return: True if the build function was run, false other
        """
        if callable(self._do_completion_test) and self._do_completion_test():
            return False

        try:
            self._do_build()
        except Exception as e:
            # We'll run the cleanup and pass the exception along
            try:
                self.cleanup()
            except:
                print(f"Target cleanup failed: target name - {self._name}")
            raise e

        return True

    def cleanup(self):
        if callable(self._do_cleanup):
            try:
                self._do_cleanup()
            except:
                print(f"Target cleanup failed: target name - {self._name}")

    def __str__(self):
        return f"{self._name}" + \
               f": {self._description}" if self._description else "" + \
               "\n\r  dependencies: " + ", ". join(self._dependency_names)

# TO DO: create specific BuildTarget extensions class for tasks like downloading files and other common tasks

class BuildTargetLoader(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def load_available_build_targets(self) -> Dict[str, BuildTarget]:
        return {}

class BasicBuildTargetLoader(BuildTargetLoader):

    def __init__(self):
        super.__init__()

        self._build_targets :  Dict[str, BuildTarget] = {}

    def add_target(self, build_target: BuildTarget) -> None:
        self._build_targets[build_target.name] = build_target

    # TO DO: add @overide when minimum python version becomes 3.12
    def load_available_build_targets(self) -> Dict[str, BuildTarget]:
        return self._build_targets

class Builder:

     def __init__(self, targets_to_run: List[str], target_loader: BuildTargetLoader, verbose: bool = False):
         self._verbose = verbose

         self._loaded_targets = target_loader.load_available_build_targets()
         
         self._verify_targets_to_run(targets_to_run)
             
         self._targets_to_run = [self._loaded_targets[t_name] for t_name in targets_to_run]

         self._verify_targets_exist_and_no_circular_dependencies()

     def _verify_targets_to_run(self, targets_to_run: List[str]) -> None:
         if len(targets_to_run) != len(set(targets_to_run)):
             raise BuildException(f"Duplicate targets found in list of targets to run")

         for target_name in targets_to_run:
             target = self._loaded_targets.get(target_name, None)

             if target is None:
                 raise BuildException(f"Could not find target named '{target_name}'")

     def _verify_targets_exist_and_no_circular_dependencies(self) -> None:
         for target in self._targets_to_run:
             self._iterate_dependency_tree(target, lambda t, s: None)

     def _iterate_dependency_tree(self, initial_target: BuildTarget, dependency_handler: Callable[[BuildTarget, str], None]) -> None:
         dep_name_stack: List[str] = []

         def i(build_target: BuildTarget):

             current_build_target_name = build_target._name
             dep_path_desc = " -> ".join(dep_name_stack + [current_build_target_name])

             if current_build_target_name in dep_name_stack:
                 raise BuildException("Circular dependency condition found: " + dep_path_desc)

             dep_name_stack.append(build_target.name)

             if build_target.dependency_names is not None:
                 for dep_name in build_target.dependency_names:
                     target = self._loaded_targets.get(dep_name, None)

                     if target is None:
                         raise BuildException(f"Could not find target named '{dep_name}'")
                     i(target)

             dependency_handler(build_target, dep_path_desc)

             dep_name_stack.pop()

         # entry point into iterative logic
         i(initial_target)

     def run(self) -> None:

         targets_run: List[BuildTarget] = []

         def run_target(target_to_run: BuildTarget, dep_path_str: str):
             if self._verbose:
                 print(f"Running target '{target_to_run.name}'...")

             # we let exceptions propagate out from build to stop the recursive build iteration
             if target_to_run.build():
                 targets_run.append(target_to_run)

         try:
             for target in self._targets_to_run:
                 self._iterate_dependency_tree(target, run_target)
         except:
             # Attempt to run cleanup in the reverse order we ran the build
             for target in reversed(targets_run):
                 if self._verbose:
                     print(f"Running cleanup for target {target.name}")
                     target.cleanup()
