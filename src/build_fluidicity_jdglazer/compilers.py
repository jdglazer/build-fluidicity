import os
from abc import ABC, abstractmethod
from typing import Tuple, List, Callable, Generator

from build_fluidicity_jdglazer.exceptions import CircularDependencyException, UnknownTargetException
from build_fluidicity_jdglazer.loaders import BuildTargetLoader
from build_fluidicity_jdglazer.targets import BuildTarget, TargetLifecycle


class BaseCompiler(ABC):

    @abstractmethod
    def compile(self, targets_to_build: List[str]) -> None:
        pass

    @abstractmethod
    def result(self) -> List[Tuple[TargetLifecycle, int]]:
        raise NotImplementedError()


class Compiler(BaseCompiler):

    def __init__(self, target_loader: BuildTargetLoader) -> None:
        super().__init__()
        self._target_loader = target_loader
        self._result: List[Tuple[BuildTarget, int]] = []

    def _iterate_targets(self, deps: List[str], deps_getter: Callable[[str], List[str]]) -> Generator[
        Tuple[str, int], None, None]:
        """
        This functions allows the iteration over a dependency tree from the dependencies
        up through the objects that depend on them. It ensures that dependencies are always
        returned before objects that depend on them

        :param deps: The starting list of strings
        :param deps_getter: A function that will convert a string name into a list of its string dependencies
        :return: A tuple contain the name of the string item and the depth of recursion
        """
        name_stack = []

        def i(ds: List[str]):

            for dep in ds:

                # This is absolutely necessary to prevent infinite loop
                if dep in name_stack:
                    raise CircularDependencyException(dep)

                name_stack.append(dep)

                sub_deps = deps_getter(dep)

                yield from i(sub_deps)

                yield (dep, len(name_stack))

                name_stack.pop()

        yield from i(deps)

    # TODO: add override in python 3.12
    def compile(self, targets_to_build: List[str]) -> None:

        def get_deps(target_name: str) -> List[str]:
            return self._target_loader.get_build_target(target_name).dependencies

        self._result.clear()

        for t_name, depth in self._iterate_targets(targets_to_build, get_deps):
            target = self._target_loader.get_build_target(t_name)
            self._result.append((target, depth))

    # TODO: add override in python 3.12
    def result(self) -> List[Tuple[BuildTarget, int]]:
        return self._result

    def show_target_hierarchy(self, verbose = False, write_to: Callable[[str], None] = print) -> None:

        for target, depth in self._result:
            write_to(("|"*(depth-1)) + "*" + target.name)
            if verbose:
                write_to(f": {target.description}")
            write_to(os.linesep)
