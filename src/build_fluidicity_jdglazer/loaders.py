from abc import ABC, abstractmethod
from typing import Dict, Optional

from build_fluidicity_jdglazer.targets import BuildTarget

# TO DO: create specific BuildTarget extensions class for tasks like downloading files and other common tasks
class BuildTargetLoader(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_build_target(self, name: str) -> Optional[BuildTarget]:
        return


class BasicBuildTargetLoader(BuildTargetLoader):

    def __init__(self):
        super().__init__()

        self._build_targets :  Dict[str, BuildTarget] = {}

    def add_target(self, build_target: BuildTarget) -> None:
        self._build_targets[build_target.name] = build_target

    # TO DO: add @override when minimum python version becomes 3.12
    def get_build_target(self, name: str) -> Optional[BuildTarget]:
        return self._build_targets.get(name, None)


# static variable to be referenced across project where targets are defined
build_target_loader = BasicBuildTargetLoader()
