#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
from abc import ABC
from typing import List

from build_fluidicity_jdglazer.targets import BuildTarget, BuildTargetBase
from build_fluidicity_jdglazer.utils import log, log_exception


class BuildTargetBaseWrapper(BuildTargetBase, ABC):

    def __init__(self, target_to_wrap: BuildTargetBase) -> None:
        super().__init__()
        self._wrapped_target = target_to_wrap

    # TODO: add override in python 3.12
    # @override
    def get_name(self) -> str:
        return self._wrapped_target.get_name()

    # TODO: add override in python 3.12
    # @override
    def get_description(self) -> str:
        return self._wrapped_target.get_description()

    # TODO: add override in python 3.12
    # @override
    def get_dependencies(self) -> List[str]:
        return self._wrapped_target.get_dependencies()


class LoggingBuildTargetBaseWrapper(BuildTargetBaseWrapper):

    def __init__(self, target_to_wrap: BuildTarget) -> None:
        super().__init__(target_to_wrap)

    # TODO: add @override in python 3.12
    # @override
    def do_build(self) -> bool:
        log(f"Building target '{self.get_name()}'", self.get_name())
        try:
            return self._wrapped_target.do_build()
        except Exception as e:
            log_exception(f"Exception raised building target '{self.get_name()}'", self.get_name())
            raise e

    # TODO: add @override in python 3.12
    # @override
    def do_cleanup(self) -> None:
        log(f"Running cleanup on target '{self.get_name()}'")
        try:
            self._wrapped_target.do_cleanup()
        except Exception as e:
            log_exception(f"Cleanup failed for target '{self.get_name()}'", self.get_name())
            raise e

    # TODO: add @override in python 3.12
    # @override
    def do_completion_test(self) -> bool:
        completion_test_result = self._wrapped_target.do_completion_test()
        log(f"Completion test result for target '{self.get_name()}': {completion_test_result}")
        return completion_test_result