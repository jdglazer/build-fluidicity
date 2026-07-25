#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org

import os
from build_fluidicity_jdglazer.builder import BuilderImpl
from build_fluidicity_jdglazer.compilers import CompilerImpl
from build_fluidicity_jdglazer.targets import BuildTarget
from build_fluidicity_jdglazer.loaders import build_target_loader

readme_file_name = "readme.md"

# define build target 'readme_created'
class CreateReadmeFile(BuildTarget):

    def __init__(self):
        super().__init__(name = "create_readme", description = "Creates readme file")

    # @override
    def do_build(self) -> None:
        # errors raised are allowed to escape as this is how the framework determines failure of the step
        with open(readme_file_name, 'w') as f:
            f.write('# readme created')

    # @override
    def do_cleanup(self) -> None:
        # Will run in the case that build fails and this step has already run
        os.remove(readme_file_name)

    # @override
    def do_completion_test(self) -> bool:
        # if the file already exists we don't want to do anything
        return os.path.exists(readme_file_name)


# define build target 'set_license'
class SetLicenseType(BuildTarget):
    file_name = "license"
    license_type = "MIT"
    license_str = f"\n\rlicense type: {license_type}"

    def __init__(self):
        super().__init__(name = "set_license",
                         description = "Creates license file and sets license in readme",
                         dependencies = ["create_readme"])

    def _is_license_str_set(self) -> bool:
        # We need to catch any errors in functions run as a part of completion tests
        try:
            with open(readme_file_name, 'r') as f:
                return self.license_str in f.read()
        except:
            return False

    def _remove_license_str(self) -> None:
        with open(readme_file_name, 'r') as f:
            readme_txt = f.read()
            readme_txt_new = readme_txt.replace(self.license_str, "")

        with open(readme_file_name, 'w') as fw:
            fw.write(readme_txt_new)

    # @override
    def do_build(self) -> None:
        with open(self.file_name, 'w') as f:
            f.write(self.license_type)

        with open(readme_file_name, 'a') as f:
            f.write(self.license_str)

    # @override
    def do_cleanup(self) -> None:
        # we also should catch errors in cleanup
        try:
            os.remove(self.file_name)
            self._remove_license_str()
        except:
            pass  # swallow error, best effort

    # @override
    def do_completion_test(self) -> bool:
        return os.path.exists(self.file_name) and self._is_license_str_set()


if __name__ == '__main__':
    # add build targets to loader
    build_target_loader.add_target(CreateReadmeFile())
    build_target_loader.add_target(SetLicenseType())

    # create compiler passing target loader
    compiler = CompilerImpl(target_loader = build_target_loader)
    # compile targets to build, 'set_license'
    compiler.compile(targets_to_build = ["set_license"])

    # create builder passing in compiler
    builder = BuilderImpl(compiler = compiler)
    # run build
    builder.run()