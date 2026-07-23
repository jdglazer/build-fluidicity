import os
from build_fluidicity_jdglazer.builder import Builder
from build_fluidicity_jdglazer.targets import BuildTarget
from build_fluidicity_jdglazer.loaders import build_target_loader

readme_file_name = "readme.md"


# define build target 'readme_created'
def define_target_create_readme_file() -> BuildTarget:
    def build() -> None:
        # errors raised are allowed to escape as this is how the framework determines failure of the step
        with open(readme_file_name, 'w') as f:
            f.write('# readme created')

    def cleanup() -> None:
        # Will run in the case that build fails and this step has already run
        os.remove(readme_file_name)

    def complete() -> bool:
        # if the file already exists we don't want to do anything
        return os.path.exists(readme_file_name)

    return BuildTarget(name="create_readme",
                       description="Creates readme file",
                       build=build,
                       completion_test=complete,
                       cleanup=cleanup)


# define build target 'set_license'
def define_target_set_license_type() -> BuildTarget:
    file_name = "license"
    license_type = "MIT"
    license_str = f"\n\rlicense type: {license_type}"

    def _is_license_str_set() -> bool:
        # We need to catch any errors in functions run as a part of completion tests
        try:
            with open(readme_file_name, 'r') as f:
                return license_str in f.read()
        except:
            return False

    def _remove_license_str() -> None:
        with open(readme_file_name, 'r') as f:
            readme_txt = f.read()
            readme_txt_new = readme_txt.replace(license_str, "")

        with open(readme_file_name, 'w') as fw:
            fw.write(readme_txt_new)

    def build() -> None:
        with open(file_name, 'w') as f:
            f.write(license_type)

        with open(readme_file_name, 'a') as f:
            f.write(license_str)

    def cleanup() -> None:
        # we also should catch errors in cleanup
        try:
            os.remove(file_name)
            _remove_license_str()
        except:
            pass  # swallow error, best effort

    def complete() -> bool:
        return os.path.exists(file_name) and _is_license_str_set()

    return BuildTarget(name="set_license",
                       description="Creates license file and sets license in readme",
                       build=build,
                       completion_test=complete,
                       cleanup=cleanup,
                       dependencies=["create_readme"])


if __name__ == '__main__':
    # add build targets to loader
    build_target_loader.add_target(define_target_create_readme_file())
    build_target_loader.add_target(define_target_set_license_type())

    # create builder and tell it to run build target named 'set_license'
    builder = Builder(target_loader=build_target_loader, targets_to_run=["set_license"])

    # run build
    builder.run()