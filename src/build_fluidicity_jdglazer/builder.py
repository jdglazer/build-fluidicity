#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
from abc import abstractmethod, ABC
from typing import List, Iterable

from build_fluidicity_jdglazer.compilers import Compiler
from build_fluidicity_jdglazer.targets import TargetLifecycle

class Builder(ABC):

    @abstractmethod
    def run(self) -> None:
        pass


    @abstractmethod
    def clean(self) -> None:
        pass


class BuilderImpl(Builder):

    def __init__(self, compiler: Compiler, clean_on_failure = True) -> None:
        self._compiler = compiler
        self._clean_on_failure = clean_on_failure

    def _build_target(self, target: TargetLifecycle) -> bool:
        """
        Runs the build function if completion test is not set or returns false

        :return: True if the build function was run, false otherwise
        """
        if target.do_completion_test():
            return False

        try:
            res = target.do_build()
            return res or res is None
        except Exception as e:
            if self._clean_on_failure:
                target.do_cleanup()
            raise e

    def _clean_targets(self, targets: Iterable[TargetLifecycle]) -> None:
        for target in targets:
            try:
                target.do_cleanup()
            except:
                pass

    # TODO: add override in python 3.12
    # @override
    def run(self) -> None:

        targets_run: List[TargetLifecycle] = []

        for target, depth in self._compiler.result():

            try:
                if self._build_target(target) and self._clean_on_failure:
                    targets_run.append(target)
            except:
                self._clean_targets(reversed(targets_run))
                break

    # TODO: add override in python 3.12
    # @override
    def clean(self) -> None:
        for target, depth in reversed(self._compiler.result()):
            try:
                target.do_cleanup()
            except:
                pass
