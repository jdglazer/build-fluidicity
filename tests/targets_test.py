import unittest
from unittest.mock import MagicMock, patch

from build_fluidicity_jdglazer.targets import BuildTarget, DirectoryCreate, ExtractZip, DownloadFile


class TestBuildTarget(unittest.TestCase):

    def test_values_set(self):
        target_name = "my-target"
        description = "this is my description"
        target = BuildTarget(build=lambda: None, name=target_name, description=description)

        self.assertEqual(target.name, target_name)
        self.assertEqual(target.description, description)

    def test_build_function_called(self):
        build_func_mock = MagicMock()
        target = BuildTarget(build=build_func_mock, name="")
        target.build()
        build_func_mock.assert_called_once()

    def test_cleanup_function_called_on_exception(self):
        build_func_mock = MagicMock(side_effect=Exception(""))
        cleanup_func_mock = MagicMock()
        target = BuildTarget(build=build_func_mock, cleanup=cleanup_func_mock, name="")
        self.assertRaises(Exception, target.build)
        cleanup_func_mock.assert_called_once()


class TestDirectoryCreate(unittest.TestCase):

    @patch('os.makedirs')
    def test_build_created_directory_call(self, mock_os_makedirs):
        dcbt = DirectoryCreate(name="test", path="/path/to/create")
        dcbt._do_build()
        mock_os_makedirs.assert_called_with(name="/path/to/create", exist_ok = True)

    @patch('os.makedirs')
    def test_build_created_directory_exception_propagates(self, mock_os_makedirs):
        mock_os_makedirs.side_effect = Exception("")

        dcbt = DirectoryCreate(name="test", path="/path/to/create")
        self.assertRaises(Exception, dcbt._build)

    @patch('shutil.rmtree')
    def test_cleanup_respects_no_delete_on_clean_setting(self, rmtree_mock):
        dcbt = DirectoryCreate(name="test", path="/path/to/create", delete_on_clean=False)
        dcbt._completion_test = lambda: True
        dcbt._do_cleanup()

        rmtree_mock.assert_not_called()

    @patch('shutil.rmtree')
    def test_cleanup_respects_delete_on_clean_setting(self, rmtree_mock):
        dcbt = DirectoryCreate(name="test", path="/path/to/create", delete_on_clean=True)
        dcbt._completion_test = lambda: True
        dcbt._do_cleanup()

        rmtree_mock.assert_called_with("/path/to/create")

    @patch('os.path.isdir')
    def test_completion_test_succeeds_when_directory_present(self, isdir_mock):
        isdir_mock.return_value = True
        dcbt = DirectoryCreate(name="test", path="/path/to/create", delete_on_clean=False)

        self.assertTrue(dcbt._completion_test())

    @patch('os.path.isdir')
    def test_completion_test_fails_when_directory_absent(self, isdir_mock):
        isdir_mock.return_value = False
        dcbt = DirectoryCreate(name="test", path="/path/to/create", delete_on_clean=False)

        self.assertFalse(dcbt._completion_test())


class TestExtractZip(unittest.TestCase):

    @patch('build_fluidicity_jdglazer.targets.extract_zip')
    def test_extract_zip_success(self, patched_extract_zip):
        ez = ExtractZip(name="test",
                        zip_path = "/path/to/file.zip",
                        extract_dir="/base/path",
                        delete_dir = None,
                        re_extract=True)
        ez._do_build()

        patched_extract_zip.assert_called_with("/path/to/file.zip", "/base/path")

    @patch('build_fluidicity_jdglazer.targets.extract_zip')
    def test_extract_zip_error_propagated(self, patched_extract_zip):
        patched_extract_zip.side_effect = Exception("")
        ez = ExtractZip(name="test",
                        zip_path="/path/to/file.zip",
                        extract_dir="/base/path",
                        delete_dir=None,
                        re_extract=True)

        self.assertRaises(Exception, ez._build)

    @patch('build_fluidicity_jdglazer.targets.extract_zip')
    @patch('os.path.exists')
    def test_build_extract_when_re_extract_enabled(self, exists_mock, patched_extract_zip):
        exists_mock.return_value = True
        ez = ExtractZip(name="test",
                        zip_path="/path/to/file.zip",
                        extract_dir="/base/path/zipex",
                        delete_dir="/base/path/zipex",
                        re_extract=True)

        ez._do_build()

        patched_extract_zip.assert_called_with("/path/to/file.zip", "/base/path/zipex")

    @patch('build_fluidicity_jdglazer.targets.extract_zip')
    @patch('os.path.exists')
    def test_build_extract_when_re_extracted_disabled(self, exists_mock, patched_extract_zip):
        exists_mock.return_value = True
        ez = ExtractZip(name="test",
                        zip_path="/path/to/file.zip",
                        extract_dir="/base/path/zipex",
                        delete_dir="/base/path/zipex",
                        re_extract=False)

        ez._do_build()

        patched_extract_zip.assert_not_called()

    @patch('shutil.rmtree')
    def test_cleanup_respects_no_delete_on_clean_setting(self, rmtree_mock):
        ez = ExtractZip(name="test",
                        zip_path="/path/to/file.zip",
                        extract_dir="/base/path/zipex",
                        delete_dir="/base/path/zipex",
                        delete_on_cleanup=False)

        ez._do_cleanup()

        rmtree_mock.assert_not_called()

    @patch('shutil.rmtree')
    @patch('os.path.isdir')
    def test_cleanup_respects_delete_on_clean_setting(self, isdir_mock, rmtree_mock):
        isdir_mock.return_value = True
        ez = ExtractZip(name="test",
                        zip_path="/path/to/file.zip",
                        extract_dir="/base/path/zipex",
                        delete_dir="/base/path/zipex",
                        delete_on_cleanup=True)

        ez._do_cleanup()

        rmtree_mock.assert_called_with("/base/path/zipex")

    @patch('shutil.rmtree')
    @patch('os.path.isdir')
    def test_no_cleanup_without_dedicated_dir_name(self, isdir_mock, rmtree_mock):
        isdir_mock.return_value = True
        ez = ExtractZip(name="test",
                        zip_path="/path/to/file.zip",
                        extract_dir="/base/path",
                        delete_dir=None,
                        delete_on_cleanup=True)

        ez._do_cleanup()

        rmtree_mock.assert_not_called()


class TestDownloadFile(unittest.TestCase):

    @patch('build_fluidicity_jdglazer.targets.download_file')
    def test_download_if_already_present_enabled(self, download_file_mock):
        df = DownloadFile(name = "test",
                          url = "/path/to/file.zip",
                          local_file_path = "/local/file.zip",
                          download_if_already_present = True)

        df._completion_test = lambda: True
        df._do_build()

        download_file_mock.assert_called_with(url="/path/to/file.zip", local_file_path="/local/file.zip")

    @patch('build_fluidicity_jdglazer.targets.download_file')
    def test_download_if_already_present_disabled(self, download_file_mock):
        df = DownloadFile(name = "test",
                          url = "/path/to/file.zip",
                          local_file_path = "/local/file.zip",
                          download_if_already_present = False)

        df._completion_test = lambda: True
        df._do_build()

        download_file_mock.assert_not_called()

    @patch('os.remove')
    @patch('os.path.isfile')
    def test_cleanup_calls_delete(self, os_isfile_mock, os_remove_mock):
        os_isfile_mock.return_value = True
        ez = DownloadFile(name="test",
                          url="/path/to/file.zip",
                          local_file_path = "/local/file.zip")
        ez._do_cleanup()
        os_remove_mock.assert_called_with("/local/file.zip")

    @patch('os.path.exists')
    def test_completion_test_calls_exists(self, path_exists_mock):
        path_exists_mock.return_value = True
        ez = DownloadFile(name="test",
                          url="/path/to/file.zip",
                          local_file_path="/local/file.zip")

        ez._do_completion_test()
        path_exists_mock.assert_called_with("/local/file.zip")


if __name__ == '__main__':
    unittest.main()