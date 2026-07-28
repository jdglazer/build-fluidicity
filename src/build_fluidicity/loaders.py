#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
from abc import ABC, abstractmethod
from typing import Dict, Callable

from build_fluidicity.exceptions import UnknownTargetException
from build_fluidicity.targets import BuildTarget


class BuildTargetLoader(ABC):
    """Abstract base type for all BuildTargetLoaders
    """
    def __init__(self):
        """Constructor
        """
        pass

    @abstractmethod
    def get_build_target(self, name: str) -> BuildTarget:
        """Gets a BuildTarget by name
        Args:
            name: name of target to find

        Returns: The build target with the given name
        """
        raise NotImplementedError()

    @abstractmethod
    def list_targets(self, verbose = False, write_to: Callable[[str], None] = print) -> None:
        """Write out information about all available targets

        Args:
            verbose: add extra details to written output
            write_to: A function that takes a string to which output will be passed

        Returns: None
        """
        pass


class BasicBuildTargetLoader(BuildTargetLoader):

    def __init__(self):
        super().__init__()

        self._build_targets :  Dict[str, BuildTarget] = {}

    # TODO: add @override when minimum python version becomes 3.12
    # @override
    def get_build_target(self, name: str) -> BuildTarget:
        assert isinstance(name, str), "Invalid target name"

        if name not in self._build_targets:
            raise UnknownTargetException(name)

        return self._build_targets[name]

    def add_target(self, build_target: BuildTarget) -> None:
        assert isinstance(build_target, BuildTarget), "Invalid target type"
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
