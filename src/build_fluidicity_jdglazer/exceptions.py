#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
from typing import Optional


class BuildException(Exception):
    """Root exception when there are internal errors building
    """
    def __init__(self, message: str = "",
                 original: Optional[Exception] = None,
                 target_name: Optional[str] = None):
        """Constructor
        Args:
            message: The error message
            original: Original exception
            target_name: Name of target to which exception pertains (if any)
        """
        # Forward the message to the parent Exception class
        super().__init__(message, original)
        self.target_name: Optional[str] = target_name


class CircularDependencyException(BuildException):
    """An exception to indicate when a target depends on itself either directly or by way of its dependencies
    """
    def __init__(self, dependency_name: str) -> None:
        """Constructor
        Args:
            dependency_name: The name of the target that depends on itself
        """
        super().__init__(f"'{dependency_name}' depends on itself", target_name=dependency_name)

class UnknownTargetException(BuildException):
    """An exception to indicate that a target requested with in build target or dependencies is not known
    to the target loader
    """
    def __init__(self, target_name: str) -> None:
        """Constructor
        Args:
            target_name: Name of target to which exception pertains (if any)
        """
        super().__init__(f"'{target_name}' is unknown", target_name=target_name)

