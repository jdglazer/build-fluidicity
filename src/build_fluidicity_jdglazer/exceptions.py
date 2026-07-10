from typing import Optional

from build_fluidicity_jdglazer.targets import BuildTarget


class BuildException(Exception):

    def __init__(self, message: str = "",
                 original: Optional[Exception] = None,
                 target: Optional[BuildTarget] = None):
        # Forward the message to the parent Exception class
        super().__init__(message, original)
        self.build_target: Optional[BuildTarget] = target
