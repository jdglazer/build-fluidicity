import os
import shutil
from abc import abstractmethod, ABC
from typing import Optional, List

from build_fluidicity_jdglazer.utils import extract_zip, download_file, log, log_exception


class MetaBuildTarget:

    def __init__(self, name: str, description: str, dependencies: List[str]) -> None:
        assert name, "Name can not be None or empty"
        self._name: str = name
        self._description: str = description
        self._dependencies: List[str] = dependencies

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def dependencies(self) -> List[str]:
        return self._dependencies

    # TODO: add @override in python 3.12
    def __str__(self) -> str:
        return f"{self.name}: {self._description}" + \
            os.linesep + "  dependencies: " + ", ". join(self.dependencies)

    # TODO: add @override in python 3.12
    def __eq__(self, other: object) -> bool:
        return isinstance(other, MetaBuildTarget) and (other.name == self.name)


class TargetLifecycle(ABC):

    @abstractmethod
    def do_build(self) -> bool:
        return True

    @abstractmethod
    def do_completion_test(self) -> bool:
        return False

    @abstractmethod
    def do_cleanup(self) -> None:
        pass


class BuildTarget(MetaBuildTarget, TargetLifecycle, ABC):

    def __init__(self, name: str,
                 description: Optional[str] = None,
                 dependencies: Optional[List[str]] = None):

        super().__init__(name, description or "", dependencies or [])


class LoggingBuildTargetWrapper(TargetLifecycle):

    def __init__(self, target_to_wrap: BuildTarget) -> None:
        self.target_to_wrap = target_to_wrap

    # TODO: add @override in python 3.12
    def do_build(self) -> bool:
        log(f"Building target '{self.target_to_wrap.name}'", self.target_to_wrap.name)
        try:
            return self.target_to_wrap.do_build()
        except Exception as e:
            log_exception(f"Exception raised building target '{self.target_to_wrap.name}'", self.target_to_wrap.name)
            raise e

    # TODO: add @override in python 3.12
    def do_cleanup(self) -> None:
        log(f"Running cleanup on target '{self.target_to_wrap.name}'")
        try:
            self.target_to_wrap.do_cleanup()
        except Exception as e:
            log_exception(f"Cleanup failed for target '{self.target_to_wrap.name}'", self.target_to_wrap.name)
            raise e

    # TODO: add @override in python 3.12
    def do_completion_test(self) -> bool:
        completion_test_result = self.target_to_wrap.do_completion_test()
        log(f"Completion test result for target '{self.target_to_wrap.name}': {completion_test_result}")
        return completion_test_result


class DirectoryCreate(BuildTarget):

    def __init__(self,
                 name: str,
                 path: str,
                 delete_on_clean = True,
                 dependencies: Optional[List[str]] = None,
                 description: Optional[str] = None) -> None:
        super().__init__(name=name,
                         description=description or f"Creates directory '{path}'",
                         dependencies=dependencies)
        self._delete_on_clean = delete_on_clean
        self._path = path

    # TODO: add @override in python 3.12
    def do_build(self) -> None:
        os.makedirs(name=self._path, exist_ok=True)

    # TODO: add @override in python 3.12
    def do_cleanup(self):
        if self._delete_on_clean and self.do_completion_test():
            try:
                shutil.rmtree(self._path)
            except Exception as e:
                log_exception(f"Error removing directory '{self._path}' on cleanup: {e}", self._name)

    # TODO: add @override in python 3.12
    def do_completion_test(self) -> bool:
        return os.path.isdir(self._path)


class ExtractZip(BuildTarget):

    def __init__(self,
                 name: str,
                 zip_path: str,
                 extract_dir: str,
                 delete_on_cleanup=True,
                 delete_dir: Optional[str] = None,
                 re_extract = True,
                 dependencies: Optional[List[str]] = None,
                 description: Optional[str] = None) -> None:
        super().__init__(name=name,
                         description=description or f"Extracts zip '{zip_path}'",
                         dependencies=dependencies)
        self._zip_path = zip_path
        self._extract_dir = extract_dir
        self._delete_dir = delete_dir
        self._re_extract = re_extract
        self._delete_on_cleanup = delete_on_cleanup

    # TODO: add @override in python 3.12
    def do_build(self) -> None:
        if self._delete_dir is not None and os.path.exists(self._delete_dir) and not self._re_extract:
            return

        # This should create the extract_dir if it doesn't yet exist
        extract_zip(self._zip_path, self._extract_dir)

    # TODO: add @override in python 3.12
    def do_cleanup(self):
        if not self._delete_on_cleanup or self._delete_dir is None:
            return

        if os.path.isdir(self._delete_dir):
            shutil.rmtree(self._delete_dir)
        elif os.path.isfile(self._delete_dir):
            os.remove(self._delete_dir)

        #TO DO: add delete logic that will look at files extracted based on zip and delete one by one

    # TODO: add @override in python 3.12
    def do_completion_test(self) -> bool:
        return self._delete_dir is not None and os.path.exists(self._delete_dir) # TO DO: empty check??


class DownloadFile(BuildTarget):

    def __init__(self, name: str, url: str, local_file_path: str, re_download = True, dependencies: Optional[List[str]] = None, description: Optional[str] = None) -> None:
        super().__init__(name=name,
                         description=description or f"Downloads file from '{url}'",
                         dependencies=dependencies)
        self._url = url
        self._local_file_path = local_file_path
        self._download_if_already_present = re_download

    # TODO: add @override in python 3.12
    def do_build(self) -> None:
        if not self._download_if_already_present and self.do_completion_test():
            return

        download_file(url=self._url, local_file_path=self._local_file_path)

    # TODO: add @override in python 3.12
    def do_cleanup(self):
        if os.path.isfile(self._local_file_path):
            os.remove(self._local_file_path)

    # TODO: add @override in python 3.12
    def do_completion_test(self) -> bool:
        return os.path.exists(self._local_file_path)
