import logging
import os
import shutil
from typing import Callable, Optional, List

from build_fluidicity_jdglazer.utils import extract_zip, download_file


class BuildTarget:

    def __init__(self, name: str, build: Callable[[], None], description: Optional[str] = None, completion_test: Callable[[], bool] = lambda: False, cleanup: Optional[Callable[[], None]] = None, dependency_names: Optional[List[str]] = None):
        self._name = name
        self._do_build = build
        self._description = description or ""
        self._do_completion_test = completion_test
        self._do_cleanup = cleanup
        self._dependency_names = dependency_names or []

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def dependency_names(self) -> List[str]:
        return self._dependency_names

    def _target_run_complete(self):
        return callable(self._do_completion_test) and self._do_completion_test()

    def build(self) -> bool:
        """
        Runs the build function if completion test is not set or returns false

        :return: True if the build function was run, false other
        """
        if self._target_run_complete():
            return False

        try:
            self._do_build()
        except Exception as e:
            # We'll run the cleanup and pass the exception along
            try:
                self.cleanup()
            except:
                logging.error("Cleanup failed for target '%s'", self._name)
            raise e

        return True


    def cleanup(self) -> None:
        if callable(self._do_cleanup):
            try:
                self._do_cleanup()
            except:
                logging.error("Cleanup failed for target '%s'", self._name)

    def __str__(self) -> str:
        return f"{self._name}" + \
               f": {self._description}" if self._description else "" + \
               "\n\r  dependencies: " + ", ". join(self._dependency_names)


class DirectoryCreate(BuildTarget):

    def __init__(self, name: str, path: str, delete_on_clean = True, dependency_names: Optional[List[str]] = None, description: Optional[str] = None) -> None:
        super().__init__(name=name, description=description, build=self._build, cleanup=self._cleanup, completion_test=self._completion_test, dependency_names=dependency_names)
        self._delete_on_clean = delete_on_clean
        self._path = path

    def _build(self) -> None:
        os.makedirs(name=self._path, exist_ok=True)

    def _cleanup(self):
        if self._delete_on_clean and not self._completion_test():
            try:
                shutil.rmtree(self._path)
            except Exception as e:
                logging.error(f"Error removing directory '{self._path}' on cleanup: {e}")

    def _completion_test(self) -> bool:
        return os.path.isdir(self._path)


class ExtractZip(BuildTarget):

    def __init__(self,
                 name: str,
                 zip_path: str,
                 extract_root_path: str,
                 dedicated_dir_name: Optional[str] = None,
                 extract_if_already_present = True,
                 delete_on_cleanup = True,
                 dependency_names: Optional[List[str]] = None,
                 description: Optional[str] = None) -> None:
        super().__init__(name=name,
                         description=description,
                         build=self._build,
                         cleanup=self._cleanup,
                         completion_test=self._completion_test,
                         dependency_names=dependency_names)
        self._zip_path = zip_path
        self._extract_root_path = extract_root_path
        self._dedicated_dir_name = dedicated_dir_name
        self._extract_if_already_present = extract_if_already_present
        self._delete_on_cleanup = delete_on_cleanup

    def _build(self) -> None:
        if not self._extract_if_already_present and self._completion_test():
            return

        extract_zip(self._zip_path, self._get_extract_path())

    def _cleanup(self):
        if not self._delete_on_cleanup:
            return

        # In this case, we have declared that we own the directory and have
        # written all out files to it. This means we can just blow the directory away
        if self._dedicated_dir_name is not None:
            shutil.rmtree(self._get_extract_path())
        #TO DO: add delete logic that will look at files extracted based on zip and delete one by one

    def _completion_test(self) -> bool:
        return os.path.exists(self._get_extract_path()) # TO DO: empty check??

    def _get_extract_path(self) -> str:
        if self._dedicated_dir_name is not None:
           return os.path.join(self._extract_root_path, self._dedicated_dir_name)

        return self._extract_root_path


class DownloadFile(BuildTarget):

    def __init__(self, name: str, url: str, local_file_path: str, download_if_already_present = True, dependency_names: Optional[List[str]] = None, description: Optional[str] = None) -> None:
        super().__init__(name=name,
                         description=description,
                         build=self._build, cleanup=self._cleanup,
                         completion_test=self._completion_test,
                         dependency_names=dependency_names)
        self._url = url
        self._local_file_path = local_file_path
        self._download_if_already_present = download_if_already_present

    def _build(self) -> None:
        if not self._download_if_already_present and self._completion_test():
            return

        download_file(url=self._url, local_file_path=self._local_file_path)

    def _cleanup(self):
        shutil.rmtree(self._local_file_path)

    def _completion_test(self) -> bool:
        return os.path.exists(self._local_file_path)
