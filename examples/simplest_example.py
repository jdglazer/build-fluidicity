from build_fluidicity_jdglazer.builder import Builder
from build_fluidicity_jdglazer.targets import BuildTarget
from build_fluidicity_jdglazer.loaders import build_target_loader

# define target one
def define_target_one() -> BuildTarget:
    def build() -> None:
        print("Build step one entered")

    return BuildTarget(name="one",
                       build=build)


# define target two
def define_target_two() -> BuildTarget:
    def build() -> None:
        print("Build step two entered")

    return BuildTarget(name="two",
                       build=build,
                       dependency_names=["one"])


if __name__ == '__main__':
    # add build targets to loader
    build_target_loader.add_target(define_target_one())
    build_target_loader.add_target(define_target_two())

    # create builder and tell it to run build target named 'two'
    builder = Builder(targets_to_run=["two"], target_loader=build_target_loader, verbose=True)

    # run build
    builder.run()