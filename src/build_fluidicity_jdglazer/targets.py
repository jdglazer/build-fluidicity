#  Copyright (c) 2026 Joshua Glazer <atrail2014@gmail.com>
#  This software is released under the MIT License.
#  https://opensource.org
#
import os
import shutil
from abc import abstractmethod, ABC
from typing import Optional, List, Callable

from build_fluidicity_jdglazer.utils import extract_zip, download_file, log_exception


class MetaBuildTarget(ABC):
    """Abstract base type
    """

    @abstractmethod
    def get_name(self) -> str:
        """Gets target name
        Returns: name of the target
        """
        return ""

    @abstractmethod
    def get_description(self) -> str:
        """Gets target description
        Returns: description of the target
        """
        return ""

    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """ Gets list of dependency names
        Returns: list of dependency target names
        """
        return []


class TargetLifecycle(ABC):
    """Abstract Base Type
    """

    @abstractmethod
    def do_build(self) -> Optional[bool]:
        """Holder for build target core logic
        Returns: None or True if function tasks completed, False if not completed
        """
        return True

    @abstractmethod
    def do_completion_test(self) -> bool:
        """Holds logic to determine if the task is completed such that it shouldn't be run
        Returns: True if task should not be run, False otherwise
        """
        return False

    @abstractmethod
    def do_cleanup(self) -> None:
        """Holds logic to clean or undo the task
        Returns: None
        """
        pass


class BuildTargetBase(MetaBuildTarget, TargetLifecycle, ABC):
    """Acts as a complete base type for build targets that can be wrapped
    """
    pass


class BuildTarget(BuildTargetBase, ABC):
    """Acts as build target base type with metadata implementations, but no target lifecycle implementations
    """
    def __init__(self, name: str,
                 description: Optional[str] = None,
                 dependencies: Optional[List[str]] = None):
        """Constructor
        Args:
            name: name of the build target
            description: description of build target
            dependencies: names of dependencies
        """
        super().__init__()
        assert isinstance(name, str), "Target name must be a string"
        assert description is None or isinstance(description, str), "Target description must be a string"
        assert dependencies is None or isinstance(dependencies, list), "Target dependencies must be a list"
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
    """A concrete implementation of BuildTarget where lifecycle functions can be injected
    """

    def __init__(self, name: str,
                 do_build: Callable[[], Optional[bool]],
                 description: Optional[str] = None,
                 dependencies: Optional[List[str]] = None,
                 do_completion_test: Optional[Callable[[], bool]] = None,
                 do_cleanup: Optional[Callable[[], None]] = None):
        """Constructor
        Args:
            name: name of the build target
            do_build: function to wrap in target do_build() implementation
            description: description of build target
            dependencies: names of dependencies
            do_completion_test: function to wrap in do_completion_test() implementation
            do_cleanup: function to wrap in do_cleanup() implementation
        """
        super().__init__(name=name, description=description, dependencies=dependencies)
        assert isinstance(do_build, Callable) or do_build is None, "do_build must be a callable or None"
        assert isinstance(do_cleanup, Callable) or do_cleanup is None, "do_cleanup must be a callable or None"
        assert isinstance(do_completion_test, Callable) or do_completion_test is None, "do_completion_test must be a callable or None"
        self._do_build = do_build
        self._do_completion_test = do_completion_test
        self._do_cleanup = do_cleanup

    def do_build(self) -> Optional[bool]:
        return self._do_build()

    def do_completion_test(self) -> bool:
        return callable(self._do_completion_test) and self._do_completion_test()

    def do_cleanup(self) -> None:
        if callable(self._do_cleanup):
            self._do_cleanup()


class DirectoryCreate(BuildTarget):
    """Build target that creates a directory
    """

    def __init__(self,
                 name: str,
                 path: str,
                 delete_on_clean = True,
                 dependencies: Optional[List[str]] = None,
                 description: Optional[str] = None) -> None:
        """Constructor
        Args:
            name: name of the build target
            path: path of directory to create
            delete_on_clean: removes directory on clean if True
            dependencies: names of dependencies
            description: description of build target
        """
        super().__init__(name=name,
                         description=description or f"Creates directory '{path}'",
                         dependencies=dependencies)
        assert isinstance(path, str), "path must be a string"
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
    """Build Target that extracts a zip file
    """

    def __init__(self,
                 name: str,
                 zip_path: str,
                 extract_dir: str,
                 delete_on_cleanup=True,
                 delete_dir: Optional[str] = None,
                 re_extract = True,
                 dependencies: Optional[List[str]] = None,
                 description: Optional[str] = None) -> None:
        """Constructor
        Args:
            name: name of the build target
            zip_path: path to zip file
            extract_dir: directory into which the zip is extracted
            delete_on_cleanup: if True, delete the extracted file or directory on cleanup, only takes effect if delete_dir argument is set
            delete_dir: The directory to delete on cleanup, this is also used to determine the result of the completion test
            re_extract: if True extract the file even if delete_dir is present
            dependencies: names of dependencies
            description: description of build target
        """
        super().__init__(name=name,
                         description=description or f"Extracts zip '{zip_path}'",
                         dependencies=dependencies)
        assert isinstance(zip_path, str), "zip_path must be a string"
        assert isinstance(extract_dir, str), "extract_dir must be a string"
        assert isinstance(delete_dir, str) or delete_dir is None, "delete_dir must be a string or None"
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
    """Build Target that downloads a file
    """

    def __init__(self,
                 name: str,
                 url: str,
                 local_file_path: str,
                 re_download = True,
                 dependencies: Optional[List[str]] = None,
                 description: Optional[str] = None) -> None:
        """Constructor
        Args:
            name: name of the build target
            url: The url to the file to download
            local_file_path: The local file to which to write the downloaded file
            re_download: if True, the file will be rewritten even if the local_file_path exists
            dependencies: names of dependencies
            description: description of build target
        """
        super().__init__(name=name,
                         description=description or f"Downloads file from '{url}'",
                         dependencies=dependencies)
        assert isinstance(url, str), "url must be a string"
        assert isinstance(local_file_path, str), "local_file_path must be a string"
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
