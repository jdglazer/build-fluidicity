import os
from build_fluidicity_jdglazer.builder import Builder
from build_fluidicity_jdglazer.targets import BuildTarget
from build_fluidicity_jdglazer.loaders import build_target_loader

readme_file_name = "readme.md"


# define build target 'readme_created'
def define_target_create_readme_file() -> BuildTarget:
    def build() -> None:
        # omitted for the purpose of cleanup example. This will never run
        pass

    def cleanup() -> None:
        # Will run in the case that build fails and this step has already run
        try:
            os.remove(readme_file_name)
        except:
            pass # best effort, we could log from here

    return BuildTarget(name="create_readme",
                       description="Creates readme file",
                       build=build,
                       cleanup=cleanup)


# define build target 'set_license'
def define_target_set_license_type() -> BuildTarget:
    file_name = "license"
    license_type = "MIT"
    license_str = f"\n\rlicense type: {license_type}"

    def _remove_license_str() -> None:
        with open(readme_file_name, 'r') as f:
            readme_txt = f.read()
            readme_txt_new = readme_txt.replace(license_str, "")

        with open(readme_file_name, 'w') as fw:
            fw.write(readme_txt_new)

    def build() -> None:
        # omitted for the purpose of cleanup example. This will never run
        pass

    def cleanup() -> None:
        # we also should catch errors in cleanup
        try:
            os.remove(file_name)
            _remove_license_str()
        except:
            pass  # swallow error, best effort

    return BuildTarget(name="set_license",
                       description="Creates license file and sets license in readme",
                       build=build,
                       cleanup=cleanup,
                       dependency_names=["create_readme"])


if __name__ == '__main__':
    # add build targets to loader
    build_target_loader.add_target(define_target_create_readme_file())
    build_target_loader.add_target(define_target_set_license_type())

    # create builder and tell it to run build target named 'set_license'
    builder = Builder(target_loader=build_target_loader, targets_to_run=["set_license"])

    # run cleanup which will run cleanup steps of the build steps above in reverse order of 'run'
    builder.clean()