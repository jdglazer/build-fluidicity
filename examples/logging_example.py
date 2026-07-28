#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
from build_fluidicity.builders import BuilderImpl
from build_fluidicity.compilers import CompilerImpl
from build_fluidicity.loaders import build_target_loader
from build_fluidicity.wrappers import LoggingBuildTargetBaseWrapper

if __name__ == '__main__':
    # assume we add build targets here to the loader, but we omit it for the
    # sake of brevity

    # create compiler
    compiler = CompilerImpl(build_target_loader, target_wrappers = [LoggingBuildTargetBaseWrapper])

    # assume we call compiler.compile(...), but we also omit it for the
    # sake of brevity

    # create builder
    builder = BuilderImpl(compiler)

    # run build
    builder.run()
