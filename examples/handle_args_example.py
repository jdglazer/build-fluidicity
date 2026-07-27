#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org

from build_fluidicity_jdglazer.cli import handle_args
from build_fluidicity_jdglazer.loaders import build_target_loader
from build_fluidicity_jdglazer.targets import CustomBuildTarget

build_target_loader.add_target(
CustomBuildTarget(name = "one",   description = "description for target one", do_build = lambda: None,
                  dependencies = ["two"])
)

build_target_loader.add_target(
CustomBuildTarget(name="two", description="description for target two", do_build=lambda: None,
                  dependencies = ["three", "four"])
)

build_target_loader.add_target(
CustomBuildTarget(name="three", description="description for target three", do_build=lambda: None,
                  dependencies=["four"])
)

build_target_loader.add_target(
CustomBuildTarget(name="four",  description="description for target four", do_build=lambda: None,
                  dependencies=["five", "six"])
)

build_target_loader.add_target(
CustomBuildTarget(name="five",  description="", do_build=lambda: None,
                  dependencies=[])
)

build_target_loader.add_target(
CustomBuildTarget(name="six",   description="", do_build=lambda: None,
                  dependencies=[])
)

if __name__ == '__main__':
    handle_args(build_target_loader)