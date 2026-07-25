#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
from abc import ABC, abstractmethod
from typing import Dict, Callable

from build_fluidicity_jdglazer.exceptions import UnknownTargetException
from build_fluidicity_jdglazer.targets import BuildTarget


class BuildTargetLoader(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_build_target(self, name: str) -> BuildTarget:
        raise NotImplementedError()

    @abstractmethod
    def list_targets(self, verbose = False, write_to: Callable[[str], None] = print) -> None:
        pass


class BasicBuildTargetLoader(BuildTargetLoader):

    def __init__(self):
        super().__init__()

        self._build_targets :  Dict[str, BuildTarget] = {}

    # TODO: add @override when minimum python version becomes 3.12
    # @override
    def get_build_target(self, name: str) -> BuildTarget:
        if name not in self._build_targets:
            raise UnknownTargetException(name)

        return self._build_targets[name]

    def add_target(self, build_target: BuildTarget) -> None:
        self._build_targets[build_target.get_name()] = build_target

    # TODO: add @override when minimum python version becomes 3.12
    # @override
    def list_targets(self, verbose = False, write_to: Callable[[str], None] = print) -> None:
        for target in self._build_targets.values():
            if verbose:
                write_to(str(target))
            else:
                write_to(target.get_name())


# static variable to be referenced across project where targets are defined
build_target_loader = BasicBuildTargetLoader()
