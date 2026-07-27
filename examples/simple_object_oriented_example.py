#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org

import os
from build_fluidicity_jdglazer.builders import BuilderImpl
from build_fluidicity_jdglazer.compilers import CompilerImpl
from build_fluidicity_jdglazer.targets import BuildTarget
from build_fluidicity_jdglazer.loaders import build_target_loader


# implement/extend BuildTarget type
class CreateReadmeFile(BuildTarget):

    readme_file_name = "readme.md"

    def __init__(self):
        super().__init__(name = "create_readme", description = "Creates readme file")

    # @override
    def do_build(self) -> None:
        # errors raised are allowed to escape as this is how the framework determines failure of the step
        with open(self.readme_file_name, 'w') as f:
            f.write('# readme created')

    # @override
    def do_cleanup(self) -> None:
        # Will run in the case that build fails and this step has already run
        os.remove(self.readme_file_name)

    # @override
    def do_completion_test(self) -> bool:
        # if the file already exists we don't want to do anything
        return os.path.exists(self.readme_file_name)


if __name__ == '__main__':
    # add CreateReadme build targets to loader
    build_target_loader.add_target(CreateReadmeFile())

    # create compiler passing target loader
    compiler = CompilerImpl(target_loader = build_target_loader)
    # compile targets to build, 'set_license'
    compiler.compile(targets_to_build = ["create_readme"])

    # create builder passing in compiler
    builder = BuilderImpl(compiler = compiler)
    # run build
    builder.run()