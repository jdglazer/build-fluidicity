
# Build Fluidicity

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## Requirements

* **Python Version:** Python >=3.10

## General Description

A lightweight python build framework designed to help configure builds based on a dependency model. Build steps can depend on the completion of other build steps. The framework will run the dependencies of a build step before the build step is run. In the case of a failure the cleanup logic of each of the build steps already run will execute in the reverse order that the steps were run.

Users define the following for each build target:
* __target name__ (required) - the name the framework identifies the target by
* __primary build logic__ (required) - a function that performs the main task of the build
* __target description__ (optional) - a string displaying more info about what the target accomplishes
* __logic to determine target completion__ (optional) - a function used to determine whether to run the target when building, target will run everytime when it's not defined
* __cleanup logic__ (optional) - a function run in the case of a build failure
* __dependencies__ (optional) - a list of names of targets that should be run before the current target

## Basic Example

```python
from build_fluidicity_jdglazer.builder import build_target_loader, Builder, BuildTarget

# define target one
def define_target_one() -> BuildTarget:

    def build() -> None:
        print("Build step one entered")

    return BuildTarget(name = "one",
                       build = build)

# define target two
def define_target_two() -> BuildTarget:

    def build() -> None:
        print("Build step two entered")
    
    return BuildTarget(name = "two",
                       build = build,
                       dependency_names= ["one"] )

if __name__ == '__main__':
    # add build targets to loader
    build_target_loader.add(define_target_one())
    build_target_loader.add(define_target_two())

    # create builder and tell it to run build target named 'two'
    builder = Builder(targets_to_run=["two"], build_target_loader=build_target_loader)
    
    # run build
    builder.run()
```

Notice that this example provided is the bare minimum needed to run build target 'two' and its dependency, 'one'. This example is provided to show the general setup. Below is a more sophisticated example.

## Extended Example

```python
import os
from build_fluidicity_jdglazer.builder import build_target_loader, Builder, BuildTarget

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

    return BuildTarget(name = "create_readme",
                       description = "Creates readme file",
                       build = build,
                       completion_test = complete,
                       cleanup = cleanup)

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
            pass # swallow error, best effort

    def complete() -> bool:
        return os.path.exists(file_name) and _is_license_str_set()
    

    return BuildTarget(name = "set_license",
                       description = "Creates license file and sets license in readme",
                       build = build,
                       completion_test = complete, 
                       cleanup = cleanup, 
                       dependency_names= ["create_readme"] )

if __name__ == '__main__':
    # add build targets to loader
    build_target_loader.add(define_target_create_readme_file())
    build_target_loader.add(define_target_set_license_type())

    # create builder and tell it to run build target named 'two'
    builder = Builder(targets_to_run=["set_license"], build_target_loader=build_target_loader)

    # run build
    builder.run()
```

The above example creates a readme file and then creates a license file adding the license type to the readme. If the readme creation fails, the license creation will not be executed. If the license creation fails, the license file and the readme file should be removed based on the cleanup steps defined. If we were to add a third target that also depended on the readme step, we ensure the readme creation would only happen once since we check for the readme's existence before creating it.

Some important notes:
* Exception Handling - We allow exceptions to propagate out of build function. This helps the framework decide that the build has failed. On the other hand, we swallow exceptions in completion tests and cleanup functions. We take the perspective that exceptions in determining completion mean it's not complete and exception in cleanup should correspond to cleanup already being done. If we want to stop cleanup on failure of a cleanup step, we can allow the exception to propagate out of cleanup functions.
* Organization - we define parent functions to return each build target. This is primarily an organization and scoping tool. This are not necessary strictly speaking.
