import os
import shutil
from typing import Callable, Optional, List

from build_fluidicity_jdglazer.utils import extract_zip, download_file, log, log_exception


class BuildTarget:

    def __init__(self, name: str,
                 build: Callable[[], None],
                 description: Optional[str] = None,
                 completion_test: Callable[[], bool] = lambda: False,
                 cleanup: Optional[Callable[[], None]] = None,
                 dependency_names: Optional[List[str]] = None):
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
            log(f"Completion test succeeded for target '{self._name}'. Will not build target.")
            return False

        try:
            self._do_build()
        except Exception as e:
            log_exception(f"Exception raised building target '{self._name}'", self._name)
            # We'll run the cleanup and pass the exception along
            self.cleanup()
            raise e

        return True

    def cleanup(self) -> None:
        if callable(self._do_cleanup):
            try:
                self._do_cleanup()
            except Exception as e:
                log_exception(f"Cleanup failed for target '{self._name}", self._name)

    def __str__(self) -> str:
        return f"{self._name}: {self._description}" + \
            "\n\r  dependencies: " + ", ". join(self._dependency_names)

    def __eq__(self, other: object) -> bool:
        return other is not None \
            and isinstance(other, BuildTarget) \
            and (other.name == self._name)

class DirectoryCreate(BuildTarget):

    def __init__(self,
                 name: str,
                 path: str,
                 delete_on_clean = True,
                 dependency_names: Optional[List[str]] = None,
                 description: Optional[str] = None) -> None:
        super().__init__(name=name,
                         description=description or f"Creates directory '{path}'",
                         build=self._build,
                         cleanup=self._cleanup,
                         completion_test=self._completion_test,
                         dependency_names=dependency_names)
        self._delete_on_clean = delete_on_clean
        self._path = path

    def _build(self) -> None:
        os.makedirs(name=self._path, exist_ok=True)

    def _cleanup(self):
        if self._delete_on_clean and self._completion_test():
            try:
                shutil.rmtree(self._path)
            except Exception as e:
                log_exception(f"Error removing directory '{self._path}' on cleanup: {e}", self._name)

    def _completion_test(self) -> bool:
        return os.path.isdir(self._path)


class ExtractZip(BuildTarget):

    def __init__(self,
                 name: str,
                 zip_path: str,
                 extract_dir: str,
                 delete_on_cleanup=True,
                 delete_dir: Optional[str] = None,
                 re_extract = True,
                 dependency_names: Optional[List[str]] = None,
                 description: Optional[str] = None) -> None:
        super().__init__(name=name,
                         description=description or f"Extracts zip '{zip_path}'",
                         build=self._build,
                         cleanup=self._cleanup,
                         completion_test=self._completion_test,
                         dependency_names=dependency_names)
        self._zip_path = zip_path
        self._extract_dir = extract_dir
        self._delete_dir = delete_dir
        self._re_extract = re_extract
        self._delete_on_cleanup = delete_on_cleanup

    def _build(self) -> None:
        if self._delete_dir is not None and os.path.exists(self._delete_dir) and not self._re_extract:
            return

        # This should create the extract_dir if it doesn't yet exist
        extract_zip(self._zip_path, self._extract_dir)

    def _cleanup(self):
        if not self._delete_on_cleanup or self._delete_dir is None:
            return

        if os.path.isdir(self._delete_dir):
            shutil.rmtree(self._delete_dir)
        elif os.path.isfile(self._delete_dir):
            os.remove(self._delete_dir)

        #TO DO: add delete logic that will look at files extracted based on zip and delete one by one

    def _completion_test(self) -> bool:
        return self._delete_dir is not None and os.path.exists(self._delete_dir) # TO DO: empty check??


class DownloadFile(BuildTarget):

    def __init__(self, name: str, url: str, local_file_path: str, download_if_already_present = True, dependency_names: Optional[List[str]] = None, description: Optional[str] = None) -> None:
        super().__init__(name=name,
                         description=description or f"Downloads file from '{url}'",
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
        if os.path.isfile(self._local_file_path):
            os.remove(self._local_file_path)

    def _completion_test(self) -> bool:
        return os.path.exists(self._local_file_path)
