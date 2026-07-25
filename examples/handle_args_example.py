#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
from build_fluidicity_jdglazer.cli import handle_args
from build_fluidicity_jdglazer.loaders import build_target_loader

if __name__ == '__main__':
    handle_args(build_target_loader)