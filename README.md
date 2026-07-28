
# Build Fluidicity

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## Requirements

* **Python Version:** >=3.10

## General Description

A lightweight python build framework built to be easily extended. 
A core principle is that an individual build task, called a build target, 
can be run, cleaned and can provide a sense of whether it should be run at any time. 
An additional core principle is that build targets can depend on the results of other build targets. 
The framework will organize builds such that all dependencies target build procedures are run first.
On the other hand, cleaning targets will run a target's clean procedure before those of its dependencies.

At its base, this framework has the series of elements described below:

| Element              | Source                                                     | Version | Purpose                                                                                                |
|----------------------|------------------------------------------------------------|---------|--------------------------------------------------------------------------------------------------------|
| Build Target         | [targets.py](src/build_fluidicity/targets.py)     | 1.0.0   | Define a build tasks and its cleanup procedures |
| Build Target Loader  | [loaders.py](src/build_fluidicity/loaders.py)     | 1.0.0   | Collectes and provides access to build targets |
| Compiler             | [compilers.py](src/build_fluidicity/compilers.py) | 1.0.0   | Converts a list of targets to run into a runnable build sequence |
| Builder              | [builders.py](src/build_fluidicity/builders.py)   | 1.0.0   | Runs a build sequence and/or its cleanup procedures |
| Build Target Wrapper | [wrappers.py](src/build_fluidicity/wrappers.py)   | 1.0.0   | Wraps build targets allowing generic extensions to build, cleanup and/or completion test functionality |

## Building Locally

### Pre-requisites
A running install of docker is necessary to continue with the below steps.

### Bash Helper Utility
This project is build on a python docker container. The image for this container can be build from the Dockerfile in the 
root directory of the project. A script called [build.sh](build.sh) is included to help make all build related tasks easier:

```bash
./build.sh -h
```

Here's the usage info:

```text
Usage: ./build.sh [options]
  -h, --help          print this usage message
  -i, --dockerimage   build docker image
  -r, --runcontainer  run docker container bash command line
  -t, --test          run python tests
  -e FILENAME         run specified example file
  -b, --build         run python package build
  -c, --clean         clean docker system cache (docker prune)
```

### Building Docker Image
The first step should be to build a docker image. This only needs to be done one time unless you are making edits to the 
[Dockerfile](Dockerfile).

```bash
./build.sh -i
```

### Running Tests
Once the image is built, we can run the python unittests as follows:

```bash
./build.sh -t
```

This will run unittests on a docker container and show the results. It will additionally build an html test coverage report
accessible at (index.html)[htmlcov/index.html]

### Building Install Packages
To build install packages, we can run the following:

```bash
./build.sh -b
```

The docker container build environment shares the project root directory as a volume and so generated build packages will 
show up in the local project root directory under [dist](dist) subdirectory.

### Accessing the Build Container Commandline
To get to a bash command line in the docker container, you can run the following:

```bash
./build.sh -r
```

This will provide access the container in the shared project root directory:

```text
 Running bash on docker container...
 root@46957618af91:/build-fluidicity#
```

This is mostly useful for testing changes to the build container itself or new build steps for the project during development.

### Building on Windows
If you wish to run build on Microsoft Windows, it is suggested you look at the contents of the [build.sh](build.sh) script. 
Many of the commands will be the same in the windows command prompt.

## Usage Examples

Example files are located in [examples](examples) folder and can be run with the following command (linux):

```bash
 PYTHON_PATH=src python examples/simplest_run_example.py
```

or, if we have built docker images, we can run this (linux):

```bash
 ./build.sh -e simplest_run_example.py
```

### Simplest Example [(simplest_example.py)](examples/simplest_run_example.py)

```python
from build_fluidicity.builders import BuilderImpl
from build_fluidicity.compilers import CompilerImpl
from build_fluidicity.targets import CustomBuildTarget
from build_fluidicity.loaders import build_target_loader


# define build target one work
def do_build_one() -> None:
    print("Build step one work")


# create build target one
target_one = CustomBuildTarget(name="one", do_build=do_build_one)

# add build target one to loader
build_target_loader.add_target(target_one)


# define target two work
def do_build_two() -> None:
    print("Build step two work")


# create build target 2
target_two = CustomBuildTarget(name="two", do_build=do_build_two, dependencies=["one"])

# add build target two to loader
build_target_loader.add_target(target_two)

if __name__ == '__main__':
    # create a compiler taking a build loader
    compiler = CompilerImpl(target_loader=build_target_loader)
    # compile with targets we wish to run
    compiler.compile(targets_to_build=["two"])

    # create builder taking the compiler
    builder = BuilderImpl(compiler=compiler)
    # run the build
    builder.run()
```

Notice that this example provided is the bare minimum needed to run build target 'two' and its dependency, 'one'. 
This example is provided to show the general setup. Below is a more sophisticated example.

### Object Oriented Example [(simple_object_oriented_example.py)](examples/simple_object_oriented_example.py)

```python
import os
from build_fluidicity.builders import BuilderImpl
from build_fluidicity.compilers import CompilerImpl
from build_fluidicity.targets import BuildTarget
from build_fluidicity.loaders import build_target_loader


# implement/extend BuildTarget type
class CreateReadmeFile(BuildTarget):
    readme_file_name = "readme.md"

    def __init__(self):
        super().__init__(name="create_readme", description="Creates readme file")

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
    compiler = CompilerImpl(target_loader=build_target_loader)
    # compile targets to build, 'set_license'
    compiler.compile(targets_to_build=["create_readme"])

    # create builder passing in compiler
    builder = BuilderImpl(compiler=compiler)
    # run build
    builder.run()
```

The above example shows an example of creating a custom build target by extending the built-in BuildTarget type and 
injecting it into the target loader. Notice that in both the above two examples, we define 2 things:

1. build target complete with required ```name``` property and, ```do_build()```, ```do_cleanup()``` and ```do_completion_check()``` 
overrides and the optional ```description``` property
2. a build target to run identified by that target's name

If we omit the first, we will get an error on the compile step. If we omit the second, the call to Builder's run method 
will not do anything.

### Cleanup Example [(simplest_clean_example.py)](examples/simplest_clean_example.py)

```python
from build_fluidicity.builders import BuilderImpl
from build_fluidicity.compilers import CompilerImpl
from build_fluidicity.targets import CustomBuildTarget
from build_fluidicity.loaders import build_target_loader

# create build target one
target_one = CustomBuildTarget(name="one",
                               do_build=lambda: None,
                               do_cleanup=lambda: print("clean one"))

# add build target one to loader
build_target_loader.add_target(target_one)

# create build target 2
target_two = CustomBuildTarget(name="two",
                               do_build=lambda: None,
                               do_cleanup=lambda: print("clean two"),
                               dependencies=["one"])

# add build target two to loader
build_target_loader.add_target(target_two)

if __name__ == '__main__':
    # create a compiler taking a build loader
    compiler = CompilerImpl(target_loader=build_target_loader)
    # compile with targets we wish to run
    compiler.compile(targets_to_build=["two"])

    # create builder taking the compiler
    builder = BuilderImpl(compiler=compiler)

    # clean the build
    builder.clean()
```

Notice that there is really no substantive difference between the code we write to run and to clean a build until the very
last line. It all comes down to which function call we make on the builder object. In this case we call ```clean()```.

### Multi-tier Dependency Example [(build_error_example.py)](examples/build_error_example.py)

Here is an example which we employ to demonstrate some of the core functionalities of build run behavior.
In this example we create 6 build targets with a more complex dependency structure. We also add a target which is already
complete, 6, and one which will throw an exception from its build method, 3. Note that each target prints
of the same message from its build and clean method, just replacing the name of the target.

If you want to test yourself, you can attempt to answer the following question: What will this program print out?

```python
from build_fluidicity.builders import BuilderImpl
from build_fluidicity.compilers import CompilerImpl
from build_fluidicity.loaders import build_target_loader
from build_fluidicity.targets import CustomBuildTarget


def raise_exc() -> None:
    print("run 3")
    raise Exception("")


_1 = CustomBuildTarget(name="1", do_build=lambda: print("run 1"),
                       do_cleanup=lambda: print("clean 1"),
                       dependencies=["2"])
_2 = CustomBuildTarget(name="2", do_build=lambda: print("run 2"),
                       do_cleanup=lambda: print("clean 2"),
                       dependencies=["3"])
# target fails in build by raising an exception
_3 = CustomBuildTarget(name="3", do_build=raise_exc,
                       do_cleanup=lambda: print("clean 3"),
                       dependencies=["4", "5"])
_4 = CustomBuildTarget(name="4", do_build=lambda: print("run 4"),
                       do_cleanup=lambda: print("clean 4"))
_5 = CustomBuildTarget(name="5", do_build=lambda: print("run 5"),
                       do_cleanup=lambda: print("clean 5"),
                       dependencies=["6"])
# target work is already complete (completion test returns true)
_6 = CustomBuildTarget(name="6", do_build=lambda: print("run 6"),
                       do_cleanup=lambda: print("clean 6"),
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
```

Running this:

```bash
./build.sh -e build_error_example.py
```

We get this output:

```text
run 4
run 5
run 3
clean 3
clean 5
clean 4
```

The dependencies of the targets are summarized as follows:

1 -> [2]

2 -> [3]

3 -> [4, 5]

4 -> []

5 -> [6]

Thus in order for 1 to build, 2 must first build. For 2 to build, 3 must first build. For 3 to build, 4 and then 5 must build.
For 4 to build, no other target must build. For 5 to build, 6 must build This is how we would determine that starting from 
build target 1, it would be target 4 that first builds. After this we would trace backward, building 6, then 5, then 3, 
then 2, then 1.

However, 3 raises an exception! Remember that raising an exception in do_build method is the indicator that the target has 
failed. Notice that no targets after, from the above-described order, have run. But wait, target 6 didn't run either. 
This should have run before 3. Notice that we have set a completion handler for target 6 that returns ```True``` no matter 
what. This means that to the framework, target 6 will not be run. It is effectively already done.

Notice that as we fail at target 3, the target ```do_cleanup()``` methods are called in the exact reverse order that we 
called the target ```do_build()``` methods. Notice that on build error, we call ```do_cleanup()``` methods only for targets
we have built including the failed target.

### Example Running Command Line Utility

The library ships with a commandline utility. For examples and more information see the section [Command Line Utility](#command-line-utility).

## Summary of Rules For Build Target Overriden Methods

The below rules should be used as a guide for writing custom extensions for ```BuildTarget```:

### __do_build()__
* Raise an ```Exception``` only to stop and fail the build
* return ```False``` to prevent cleanup on failure, ```True``` or ```None``` otherwise

### __do_cleanup()__
* Write logic robust enough to handle the conditions that ```do_build()``` has not run
* Write logic robust enough to handle the conditions under which ```do_completion_test()``` returns ```True```

### __do_completion_test()__
* Should return ```True``` in the case where target should not be run again or where it is at least unnecessary
* Returning ```False``` should only be done if the ```do_build()``` logic is robust enough to be called multiple times
without ```do_clean()``` being called between

## Command Line Utility

The library ships with a command line utility that is called in a Python program as follows:

```python
from build_fluidicity.cli import handle_args
from build_fluidicity.loaders import build_target_loader
from build_fluidicity.targets import CustomBuildTarget

# add targets to loader here

if __name__ == '__main__':
    handle_args(build_target_loader)
```

We can run the example program, [handle_args_example.py](examples/handle_args_example.py), on our docker build container:

```bash
./build.sh -r
Running bash on docker container...
root@76a7b11aba63:/build-fluidicity# PYTHONPATH=src python examples/handle_args_example.py -h
```

We get the following usage message:

```text
usage: handle_args_example.py [-h] (-list | -run target name [target name ...] | -clean target name [target name ...]) [--dry] [--verbose]

Build Fluidicity commandline application

options:
  -h, --help            show this help message and exit
  -list                 Lists all available build targets
  -run target name [target name ...]
                        Run build targets specified by name
  -clean target name [target name ...]
                        Run clean on targets specified by name
  --dry                 Iterate through build steps without running. This will print information on build steps
  --verbose             List or log more details
```

This utility exposes much of the base functionality of this framework on the command line. For example, we might run the 
following to understand what build targets we have available (still on our docker container bash interface):

```bash
PYTHONPATH=src python examples/handle_args_example.py -list
```

We will see the following:

```text
one
two
three
four
five
six
```
This shows us what build targets are available. Now let's say we decide we want to run build target one, but we want to
get an idea of what build targets will run and in what order due to dependencies. We would simply run the following:

```bash
PYTHONPATH=src python examples/handle_args_example.py -run one --dry
```

And we would see this:

```text
| | | | *five
| | | | *six
| | | *four
| | *three
| | | *five
| | | *six
| | *four
| *two
*one
```

From top to bottom, this will be the order that the targets will run. Note that dependencies are indented above their 
parent build targets. In this output the target(s) we called out will always be at the bottom as all dependencies must
be run first. Now lets say we're satisfied, we'll go ahead and run this:

```bash
PYTHONPATH=src python examples/handle_args_example.py -run one --verbose
```

We see the following:

```text
Mon Jul 27 23:38:17 2026 [engine] Completion test result for target 'five': False
Mon Jul 27 23:38:17 2026 [target: five] Building target 'five'
Mon Jul 27 23:38:17 2026 [engine] Completion test result for target 'six': False
Mon Jul 27 23:38:17 2026 [target: six] Building target 'six'
Mon Jul 27 23:38:17 2026 [engine] Completion test result for target 'four': False
Mon Jul 27 23:38:17 2026 [target: four] Building target 'four'
Mon Jul 27 23:38:17 2026 [engine] Completion test result for target 'three': False
Mon Jul 27 23:38:17 2026 [target: three] Building target 'three'
Mon Jul 27 23:38:17 2026 [engine] Completion test result for target 'five': False
Mon Jul 27 23:38:17 2026 [target: five] Building target 'five'
Mon Jul 27 23:38:17 2026 [engine] Completion test result for target 'six': False
Mon Jul 27 23:38:17 2026 [target: six] Building target 'six'
Mon Jul 27 23:38:17 2026 [engine] Completion test result for target 'four': False
Mon Jul 27 23:38:17 2026 [target: four] Building target 'four'
Mon Jul 27 23:38:17 2026 [engine] Completion test result for target 'two': False
Mon Jul 27 23:38:17 2026 [target: two] Building target 'two'
Mon Jul 27 23:38:17 2026 [engine] Completion test result for target 'one': False
Mon Jul 27 23:38:17 2026 [target: one] Building target 'one'
```

Notice that the targets ran in the same order we were shown during the dry run. Finally, lets imagine we want to clean 
the build. We could run this:

```bash
PYTHONPATH=src python examples/handle_args_example.py -clean one --verbose
```

We get the following output:

```text
Mon Jul 27 23:40:43 2026 [engine] Running cleanup on target 'one'
Mon Jul 27 23:40:43 2026 [engine] Running cleanup on target 'two'
Mon Jul 27 23:40:43 2026 [engine] Running cleanup on target 'four'
Mon Jul 27 23:40:43 2026 [engine] Running cleanup on target 'six'
Mon Jul 27 23:40:43 2026 [engine] Running cleanup on target 'five'
Mon Jul 27 23:40:43 2026 [engine] Running cleanup on target 'three'
Mon Jul 27 23:40:43 2026 [engine] Running cleanup on target 'four'
Mon Jul 27 23:40:43 2026 [engine] Running cleanup on target 'six'
Mon Jul 27 23:40:43 2026 [engine] Running cleanup on target 'five'
```

Notice that the clean ran in the reverse order that the dry run showed us.

## Concepts For Future Extensions

### BuildTarget

Add more BuildTarget extensions that handle specific tasks. There is a virtually unlimited range of possibilities here.

### BuildTargetLoader

Add new schemes for finding BuildTargets in a Python runtime environment. For example, a loader than find all BuildTarget
types in a specific package or module. Another could be a loader that brings multiple sub-loaders together. Another concept
would create a loader that would store only class types and instantiate targets on an as-needed basis.

### Compiler

Concentrate on improving the capabilities of the existing compiler implementation.

### Builder

Concentrate on improving the capabilities of the existing builder implementation. We also might consider adding a build
context object for preserving state across all steps of the build and making it available to build targets. We could imagine
add a new lifecycle function to build targets that would set build context.

### BuildTargetBaseWrappers

Add wrapper implementations that perform diagnostic functions such as measuring time for a particular target to run.