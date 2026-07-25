from build_fluidicity_jdglazer.targets import BuildTarget, BuildTargetBase
from build_fluidicity_jdglazer.wrappers import BuildTargetBaseWrapper


class UltraSimpleBuildTargetSub(BuildTarget):

    def __init__(self, name, description= None, dependencies= None):
        super().__init__(name, description, dependencies)

    def do_build(self) -> bool:
        return True

    def do_cleanup(self) -> None:
        pass

    def do_completion_test(self) -> bool:
        return False


class SimpleClassA(BuildTargetBaseWrapper):

    def __init__(self, btb: BuildTargetBase):
        super().__init__(btb)

    def do_build(self) -> bool:
        pass

    def do_completion_test(self) -> bool:
        pass

    def do_cleanup(self) -> None:
        pass


class SimpleClassB(BuildTargetBaseWrapper):

    def __init__(self, btb: BuildTargetBase):
        super().__init__(btb)

    def do_build(self) -> bool:
        return True

    def do_completion_test(self) -> bool:
        return False

    def do_cleanup(self) -> None:
        pass
