import os
import shutil
from abc import abstractmethod, ABC
from typing import Optional, List, Callable

from build_fluidicity_jdglazer.utils import extract_zip, download_file, log_exception


class MetaBuildTarget(ABC):

    @abstractmethod
    def get_name(self) -> str:
        return ""

    @abstractmethod
    def get_description(self) -> str:
        return ""

    @abstractmethod
    def get_dependencies(self) -> List[str]:
        return []


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


class BuildTargetBase(MetaBuildTarget, TargetLifecycle, ABC):

    def __init__(self):
        pass


class BuildTarget(BuildTargetBase, ABC):

    def __init__(self, name: str,
                 description: Optional[str] = None,
                 dependencies: Optional[List[str]] = None):
        super().__init__()
        self._name = name
        self._description = description or ""
        self._dependencies = dependencies or []

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._description

    def get_dependencies(self) -> List[str]:
        return self._dependencies

    # TODO: add @override in python 3.12
    # @override
    def __str__(self) -> str:
        return f"{self._name}: {self._description}" + \
            os.linesep + "  dependencies: " + ", ".join(self._dependencies)

    # TODO: add @override in python 3.12
    # @override
    def __eq__(self, other: object) -> bool:
        return isinstance(other, MetaBuildTarget) and (other.get_name() == self._name)


class CustomBuildTarget(BuildTarget):

    def __init__(self, name: str,
                 do_build: Callable[[], bool],
                 description: Optional[str] = None,
                 dependencies: Optional[List[str]] = None,
                 do_completion_test: Optional[Callable[[], bool]] = None,
                 do_cleanup: Optional[Callable[[], None]] = None):
        super().__init__(name=name, description=description, dependencies=dependencies)
        self._do_build = do_build
        self._do_completion_test = do_completion_test
        self._do_cleanup = do_cleanup

    def do_build(self) -> bool:
        return self._do_build()

    def do_completion_test(self) -> bool:
        return callable(self._do_completion_test) and self._do_completion_test()

    def do_cleanup(self) -> None:
        if callable(self._do_cleanup):
            self._do_cleanup()


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
