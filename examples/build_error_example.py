#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
from build_fluidicity_jdglazer.builder import BuilderImpl
from build_fluidicity_jdglazer.compilers import CompilerImpl
from build_fluidicity_jdglazer.loaders import build_target_loader
from build_fluidicity_jdglazer.targets import CustomBuildTarget


def raise_exc() -> None:
    print("run 3")
    raise Exception("")


_1 = CustomBuildTarget(name = "1",   do_build=lambda: print("run 1"),
                                     do_cleanup = lambda: print("clean 1"),
                                     dependencies=["2"])
_2 = CustomBuildTarget(name = "2",   do_build=lambda: print("run 2"),
                                     do_cleanup = lambda: print("clean 2"),
                                     dependencies=["3"])
# target fails in build by raising an exception
_3 = CustomBuildTarget(name = "3",   do_build=raise_exc,
                                     do_cleanup = lambda: print("clean 3"),
                                     dependencies=["4", "5"])
_4 = CustomBuildTarget(name = "4",   do_build=lambda: print("run 4"),
                                     do_cleanup = lambda: print("clean 4"))
_5 = CustomBuildTarget(name = "5",   do_build=lambda: print("run 5"),
                                     do_cleanup = lambda: print("clean 5"),
                                     dependencies=["6"])
# target work is already complete (completion test returns true)
_6 = CustomBuildTarget(name = "6",   do_build=lambda: print("run 6"),
                                     do_cleanup = lambda: print("clean 6"),
                                     do_completion_test=lambda: True)

if __name__ == '__main__':
    # If we compile to build 1 only:
    # build order: 4 > 6 > 5 > 3 > 2 > 1
    # facts:       6 - already complete, 3 - raises an exception
    # Questions:
    #   1. Which targets will run and in what order?
    #      A: 4 > 5 > 3
    #   2. Which targets will be cleaned on exception from target 3 and in what order?
    #      A: 3 > 5 > 4

    build_target_loader.add_target(_1)
    build_target_loader.add_target(_2)
    build_target_loader.add_target(_3)
    build_target_loader.add_target(_4)
    build_target_loader.add_target(_5)
    build_target_loader.add_target(_6)

    compiler = CompilerImpl(build_target_loader)
    compiler.compile(["1"])

    BuilderImpl(compiler).run()


