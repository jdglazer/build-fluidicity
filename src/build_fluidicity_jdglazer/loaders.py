import os
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Callable

from build_fluidicity_jdglazer.exceptions import UnknownTargetException
from build_fluidicity_jdglazer.targets import BuildTarget

# TO DO: create specific BuildTarget extensions class for tasks like downloading files and other common tasks
class BuildTargetLoader(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_build_target(self, name: str) -> BuildTarget:
        raise NotImplementedError()

    @abstractmethod
    def get_all_targets(self) -> Iterable[BuildTarget]:
        return []

    @abstractmethod
    def list_targets(self, verbose = False, write_to: Callable[[str], None] = print) -> None:
        pass


class BasicBuildTargetLoader(BuildTargetLoader):

    def __init__(self):
        super().__init__()

        self._build_targets :  Dict[str, BuildTarget] = {}

    def add_target(self, build_target: BuildTarget) -> None:
        self._build_targets[build_target.name] = build_target

    # TO DO: add @override when minimum python version becomes 3.12
    def get_build_target(self, name: str) -> BuildTarget:
        if name not in self._build_targets:
            raise UnknownTargetException(name)

        return self._build_targets[name]

    def get_all_targets(self) -> Iterable[BuildTarget]:
        return self._build_targets.values()

    def list_targets(self, verbose = False, write_to: Callable[[str], None] = print) -> None:
        for target in self.get_all_targets():
            if verbose:
                write_to(str(target))
            else:
                write_to(target.name)

            write_to(os.linesep)


# static variable to be referenced across project where targets are defined
build_target_loader = BasicBuildTargetLoader()
