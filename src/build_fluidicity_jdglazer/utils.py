import sys
import time
import traceback
from typing import Callable, Optional
from urllib.request import urlopen
from zipfile import ZipFile, ZipInfo


def _get_log_target_name(build_target_name: Optional[str]) -> str:
    return f"target: {build_target_name}" if build_target_name else "engine"

def log(message: str, build_target_name: Optional[str] = None) -> None:
    print(f"{time.asctime()} [{_get_log_target_name(build_target_name)}] {message}")

def log_exception(message: str = "", build_target_name: Optional[str] = None) -> None:
    log(f"EXCEPTION! {message}", build_target_name)
    exc_type, exc, exc_traceback = sys.exc_info()
    if exc is not None:
        print("".join(traceback.format_exception(exc)))

def iterate_zip_entries(zip_path: str, on_entry: Callable[[ZipFile, ZipInfo], None]) -> None:
    with ZipFile(zip_path) as zf:

        for info in zf.infolist():
            on_entry(zf, info)

def extract_zip(zip_path: str, extract_root_path: str) -> None:

    def ext(zip_file: ZipFile, zip_info: ZipInfo) -> None:
        zip_file.extract(member=zip_info, path=extract_root_path)

    iterate_zip_entries(zip_path, ext)

def download_file(url: str, local_file_path: str, on_progress: Optional[Callable[[int], None]] = None) -> None:
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