from abc import ABC
from typing import Callable, Dict, List, Optional

class BuildException(Exception):

    def __init__(self, message: str = ""):
        self.message = message
        # Forward the message to the parent Exception class
        super().__init__(self.message)

class BuildTarget:

    def __init__(self, name: str, build: Callable[[], None], description: Optional[str] = None, completion_test: Callable[[], bool] = lambda: False, cleanup: Optional[Callable[[], None]] = None, dependency_names: Optional[List[str]] = None):
        self.name = name
        self.build = build
        self.description = description
        self.completion_test = completion_test
        self.cleanup = cleanup
        self.dependency_names = dependency_names

class BuildTargetLoader(ABC):

    def __init__(self):
        pass

    def load_available_build_targets(self) -> Dict[str, BuildTarget]:
        return {}

class BuildTree:

     def __init__(self, targets_to_run: List[str], target_loader: BuildTargetLoader, verbose: bool = False):
         self._verbose = verbose

         self._loaded_targets = target_loader.load_available_build_targets()
         
         self._verify_targets_to_run(targets_to_run)
             
         self.targets_to_run = map(lambda t_name: self._loaded_targets[t_name], targets_to_run)

         self._verify_targets_exist_and_no_circular_dependencies()

     def _verify_targets_to_run(self, targets_to_run: List[str]):
         if len(targets_to_run) != len(set(targets_to_run)):
             raise BuildException(f"Duplicate targets found in list of targets to run")

         for target_name in targets_to_run:
             target = self._loaded_targets.get(target_name, None)

             if target is None:
                 raise BuildException(f"Could not find target named '{target_name}'")

     def _verify_targets_exist_and_no_circular_dependencies(self):
         for target in self.targets_to_run:
             self._iterate_dependency_tree(target, lambda t, s: None)

     def _iterate_dependency_tree(self, initial_target: BuildTarget, dependency_handler: Callable[[BuildTarget, str], None]) -> None:
         dep_name_stack: List[str] = []

         def i(build_target: BuildTarget):

             current_build_target_name = build_target.name
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

         i(initial_target)

     def run(self):

         targets_run: List[BuildTarget] = []

         def run_target(target_to_run: BuildTarget, dep_path_str: str):
             if self._verbose:
                 print(f"Checking target for dependency path: {dep_path_str}")

             runner = BuildTargetRunner(target_to_run)
             runner.run()

             if runner.ran_target:
                 targets_run.append(target_to_run)

             if runner.failed:
                 # This has the effect of unwinding the stack to get us out of recursive logic
                 raise BuildException("Failure running target")

         try:
             for target in self.targets_to_run:
                 self._iterate_dependency_tree(target, run_target)
         except:
             # Attempt to run cleanup in the reverse order we ran the build
             for target in reversed(targets_run):
                 if target.cleanup is not None:
                     # this is really a best effort kind of thing. We'll catch exceptions and move on
                     try:
                         target.cleanup()
                     except:
                         print(f"Target cleanup failed: target name - {target.name}")

class BuildTargetRunner:

    def __init__(self, target_to_run: BuildTarget):
        self.target_to_run = target_to_run
        self.ran_target = False
        self.failed = False

    def run(self):
        # we'll see if target is already considered complete to avoid duplicate runs
        if self.target_to_run.completion_test():
            return

        self.ran_target = True
        try:
            self.target_to_run.build()
        except:
            print(f"Error caught running target '{self.target_to_run.name}'")
            self.failed = True

if __name__ == '__main__':
    pass