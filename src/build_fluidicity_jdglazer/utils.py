#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
import sys
import time
import traceback
from typing import Callable, Optional, List, Generator, Tuple
from urllib.request import urlopen
from zipfile import ZipFile, ZipInfo

from build_fluidicity_jdglazer.exceptions import CircularDependencyException


def _get_log_target_name(build_target_name: Optional[str]) -> str:
    return f"target: {build_target_name}" if build_target_name else "engine"


def log(message: str, build_target_name: Optional[str] = None) -> None:
    """Basic print logger

    Args:
        message: Message to log
        build_target_name: build target name for which message is pertinent, if any

    Returns: None
    """
    print(f"{time.asctime()} [{_get_log_target_name(build_target_name)}] {message}")


def log_exception(message: str = "", build_target_name: Optional[str] = None) -> None:
    """Basic exception print logger

    Args:
        message: Error message
        build_target_name: build target name for which message is pertinent, if any

    Returns: None
    """
    log(f"EXCEPTION! {message}", build_target_name)
    exc_type, exc, exc_traceback = sys.exc_info()
    if exc is not None:
        print("".join(traceback.format_exception(exc)))


def _iterate_zip_entries(zip_path: str, on_entry: Callable[[ZipFile, ZipInfo], None]) -> None:
    with ZipFile(zip_path) as zf:

        for info in zf.infolist():
            on_entry(zf, info)


def extract_zip(zip_path: str, extract_root_path: str) -> None:
    """Extracts zip file to specified directory

    Args:
        zip_path: The path to the zip file
        extract_root_path: The directory to which the zip will be extracted

    Returns: None
    """

    def ext(zip_file: ZipFile, zip_info: ZipInfo) -> None:
        zip_file.extract(member=zip_info, path=extract_root_path)

    _iterate_zip_entries(zip_path, ext)


def download_file(url: str, local_file_path: str, on_progress: Optional[Callable[[int], None]] = None) -> None:
    """Downloads a file from an http(s) address

    Args:
        url: Url to file download
        local_file_path: The local file to write download to
        on_progress: A handler callback that is called with total bytes downloaded

    Returns: None
    """
    with urlopen(url=url) as response:

        if response.status >= 300:
            print(f"Error status returned attempting to download file: {url}")

        total_downloaded = 0

        buffer = bytearray(2000)

        with open(local_file_path, 'wb') as local_file:

            while (bytes_read := response.readinto(buffer)) > 0:
                local_file.write(buffer[:bytes_read])

                total_downloaded += bytes_read

                if callable(on_progress):
                    on_progress(total_downloaded)

# TODO: convert to generic function in python 3.12. See example signature below
# def iterate_items[T](deps: List[T], deps_getter: Callable[[T], List[T]]) -> Generator[
#    Tuple[T, int], None, None]:
def iterate_items(deps: List[str], deps_getter: Callable[[str], List[str]]) -> Generator[
    Tuple[str, int], None, None]:
    """This functions allows the iteration over a dependency tree from the dependencies
    up through the objects that depend on them. It ensures that dependencies are always
    returned before objects that depend on them

    Args:
        deps: The starting list of strings
        deps_getter: A function that will convert a string name into a list of its string dependencies

    Returns: A tuple containing the name of the string item and the depth of recursion
    """
    name_stack = []

    def i(ds: List[str]):

        for dep in ds:

            # This is absolutely necessary to prevent infinite loop
            if dep in name_stack:
                raise CircularDependencyException(dep)

            name_stack.append(dep)

            sub_deps = deps_getter(dep)

            yield from i(sub_deps)

            yield dep, len(name_stack)

            name_stack.pop()

    yield from i(deps)