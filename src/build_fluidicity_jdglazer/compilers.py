#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
from abc import ABC, abstractmethod
from typing import Tuple, List, Callable, Optional, Type

from build_fluidicity_jdglazer.loaders import BuildTargetLoader
from build_fluidicity_jdglazer.targets import BuildTarget, TargetLifecycle, BuildTargetBase
from build_fluidicity_jdglazer.utils import iterate_items
from build_fluidicity_jdglazer.wrappers import BuildTargetBaseWrapper


class Compiler(ABC):

    @abstractmethod
    def compile(self, targets_to_build: List[str]) -> None:
        pass

    @abstractmethod
    def result(self) -> List[Tuple[TargetLifecycle, int]]:
        raise NotImplementedError()

    @abstractmethod
    def show_target_hierarchy(self, verbose: bool = False, write_to: Callable[[str], None] = print) -> None:
        pass

class CompilerImpl(Compiler):

    def __init__(self, target_loader: BuildTargetLoader, target_wrappers: Optional[List[Type[BuildTargetBaseWrapper]]] = None) -> None:
        super().__init__()
        self._target_loader = target_loader
        self._target_wrappers = target_wrappers
        self._result: List[Tuple[BuildTarget, int]] = []

    # TODO: add override in python 3.12
    # @override
    def compile(self, targets_to_build: List[str]) -> None:

        def get_deps(target_name: str) -> List[str]:
            return self._target_loader.get_build_target(target_name).get_dependencies()

        self._result.clear()

        for t_name, depth in iterate_items(targets_to_build, get_deps):
            target = self._target_loader.get_build_target(t_name)
            self._result.append((target, depth))

    def _wrap_build_target(self, target: BuildTargetBase) -> BuildTargetBase:
        if self._target_wrappers is None:
            return target

        last_target = target

        for wrapper in self._target_wrappers:
            last_target = wrapper(last_target)

        return last_target

    # TODO: add override in python 3.12
    # @override
    def result(self) -> List[Tuple[TargetLifecycle, int]]:
        result = []
        for target, depth in self._result:
            result.append( (self._wrap_build_target(target), depth ) )
        return result

    # TODO: add override in python 3.12
    # @override
    def show_target_hierarchy(self, verbose = False, write_to: Callable[[str], None] = print) -> None:

        for target, depth in self._result:
            line = ("| "*(depth-1)) + \
                   f"*{target.get_name()}" + \
                   (f": {target.get_description()}" if verbose else "")
            write_to(line)
