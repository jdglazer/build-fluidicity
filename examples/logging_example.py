#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
from build_fluidicity_jdglazer.builder import BuilderImpl
from build_fluidicity_jdglazer.compilers import CompilerImpl
from build_fluidicity_jdglazer.loaders import build_target_loader
from build_fluidicity_jdglazer.wrappers import LoggingBuildTargetBaseWrapper

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
