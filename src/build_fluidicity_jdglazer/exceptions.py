from typing import Optional

from build_fluidicity_jdglazer.targets import BuildTarget


class BuildException(Exception):

    def __init__(self, message: str = "",
                 original: Optional[Exception] = None,
                 target: Optional[BuildTarget] = None):
        # Forward the message to the parent Exception class
        super().__init__(message, original)
        self.build_target: Optional[BuildTarget] = target


class CircularDependencyException(BuildException):

    def __init__(self, dependency_name: str) -> None:
        super().__init__(f"'{dependency_name}' dependends on itself")

class UnknownTargetException(BuildException):

    def __init__(self, target_name: str) -> None:
        super().__init__(f"'{target_name}' is unknown")

