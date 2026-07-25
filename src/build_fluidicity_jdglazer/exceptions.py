from typing import Optional


class BuildException(Exception):

    def __init__(self, message: str = "",
                 original: Optional[Exception] = None,
                 target_name: Optional[str] = None):
        # Forward the message to the parent Exception class
        super().__init__(message, original)
        self.target_name: Optional[str] = target_name


class CircularDependencyException(BuildException):

    def __init__(self, dependency_name: str) -> None:
        super().__init__(f"'{dependency_name}' depends on itself", target_name=dependency_name)

class UnknownTargetException(BuildException):

    def __init__(self, target_name: str) -> None:
        super().__init__(f"'{target_name}' is unknown", target_name=target_name)

