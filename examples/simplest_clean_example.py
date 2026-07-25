#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#

from build_fluidicity_jdglazer.builder import BuilderImpl
from build_fluidicity_jdglazer.compilers import CompilerImpl
from build_fluidicity_jdglazer.targets import CustomBuildTarget
from build_fluidicity_jdglazer.loaders import build_target_loader


# create build target one
target_one = CustomBuildTarget(name="one",
                               do_build = lambda: None,
                               do_cleanup = lambda: print("clean one"))

# add build target one to loader
build_target_loader.add_target(target_one)

# create build target 2
target_two = CustomBuildTarget(name = "two",
                               do_build = lambda: None,
                               do_cleanup = lambda: print("clean two"),
                               dependencies = ["one"])

# add build target two to loader
build_target_loader.add_target(target_two)


if __name__ == '__main__':
    # create a compiler taking a build loader
    compiler = CompilerImpl(target_loader = build_target_loader)
    # compile with targets we wish to run
    compiler.compile(targets_to_build = ["two"])

    # create builder taking the compiler
    builder = BuilderImpl(compiler = compiler)

    # run the build
    builder.clean()