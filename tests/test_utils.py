from build_fluidicity_jdglazer.targets import BuildTarget


class UltraSimpleBuildTargetSub(BuildTarget):

    def __init__(self, name, description= None, dependencies= None):
        super().__init__(name, description, dependencies)

    def do_build(self) -> bool:
        return True

    def do_cleanup(self) -> None:
        pass

    def do_completion_test(self) -> bool:
        return False