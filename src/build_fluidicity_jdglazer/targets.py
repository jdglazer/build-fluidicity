from typing import Callable, Optional, List


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

    def _target_run_complete(self):
        return callable(self._do_completion_test) and self._do_completion_test()

    def build(self) -> bool:
        """
        Runs the build function if completion test is not set or returns false

        :return: True if the build function was run, false other
        """
        if self._target_run_complete():
            return False

        try:
            self._do_build()
        except Exception as e:
            # We'll run the cleanup and pass the exception along
            try:
                self.cleanup()
            except:
                print(f"Cleanup failed for target '{self._name}'")
            raise e

        return True


    def cleanup(self) -> None:
        if callable(self._do_cleanup):
            try:
                self._do_cleanup()
            except:
                print(f"Cleanup failed for target '{self._name}'")

    def __str__(self) -> str:
        return f"{self._name}" + \
               f": {self._description}" if self._description else "" + \
               "\n\r  dependencies: " + ", ". join(self._dependency_names)
