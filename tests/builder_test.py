import unittest
from typing import Optional
from unittest.mock import MagicMock, call

from build_fluidicity_jdglazer.builder import BuilderImpl
from build_fluidicity_jdglazer.exceptions import BuildException


class TestBuilderImpl(unittest.TestCase):

    def setUp(self):
        self._compiler_mock = MagicMock()
        self._compiler_mock.result = MagicMock()
        self._compiler_mock.result.return_value = []

        self._builder = BuilderImpl(self._compiler_mock)

    def addTarget(self,
                  do_build_return = True,
                  do_build_effect: Optional[Exception] = None,
                  do_completion_return = False,
                  do_cleanup_effect: Optional[Exception] = None,
                  depth = 1) -> MagicMock:

        do_build = MagicMock()
        do_build.return_value = do_build_return
        if do_build_effect is not None:
            do_build.side_effect = do_build_effect

        do_completion_test = MagicMock()
        do_completion_test.return_value = do_completion_return

        do_cleanup = MagicMock()
        if do_cleanup_effect is not None:
            do_cleanup.side_effect = do_cleanup_effect

        target = MagicMock()
        target.do_build = do_build
        target.do_completion_test = do_completion_test
        target.do_cleanup = do_cleanup

        self._compiler_mock.result.return_value.append((target, depth))

        return target

    def test_build_runs_targets_completion_check_and_build_methods_only(self):
        target = self.addTarget(do_build_return = True,
                       do_completion_return = False)

        # verify do_build return transmitted
        self.assertTrue(self._builder._build_target(target))

        target.do_completion_test.assert_called_once()
        target.do_build.assert_called_once()
        target.do_cleanup.assert_not_called()

    def test_build_does_not_run_build_nor_clean_methods_on_true_completion_test(self):
        target = self.addTarget(do_completion_return=True)

        # verify false returned when target not run due to already being complete
        self.assertFalse(self._builder._build_target(target))

        target.do_completion_test.assert_called_once()
        target.do_build.assert_not_called()
        target.do_cleanup.assert_not_called()

    def test_do_build_false_returned(self):
        target = self.addTarget(do_build_return=False)

        self.assertFalse(self._builder._build_target(target))

        # for good measure, let's make sure false return from do_build is not enough to trigger cleanup
        target.do_cleanup.assert_not_called()

    def test_do_build_exc_propagates_and_triggers_cleanup_by_default(self):
        target = self.addTarget(do_build_effect=BuildException(""))

        self.assertRaises(BuildException, self._builder._build_target, target)

        target.do_cleanup.assert_called_once()

    def test_builder_response_cleanup_on_error_parameter(self):
        target = self.addTarget(do_build_effect=BuildException(""))

        builder = BuilderImpl(self._compiler_mock, clean_on_failure=False)

        try:
            builder._build_target(target)
        except:
            # swallow the error, it's not important for this test
            pass

        target.do_cleanup.assert_not_called()

    def test_run_all_targets(self):
        target1 = self.addTarget()
        target2 = self.addTarget()
        target3_already_done = self.addTarget(do_completion_return=True)
        target4 = self.addTarget()

        self._builder.run()

        target1.do_build.assert_called_once()
        target2.do_build.assert_called_once()
        target3_already_done.do_build.assert_not_called()
        target4.do_build.assert_called_once()

    def test_target_run_order_respected(self):
        targetfirst = self.addTarget()
        targetsecond = self.addTarget()
        targetthird = self.addTarget()
        targetfourth = self.addTarget()

        manager_mock = MagicMock()
        manager_mock.attach_mock(targetfirst, "targetfirst")
        manager_mock.attach_mock(targetsecond, "targetsecond")
        manager_mock.attach_mock(targetthird, "targetthird")
        manager_mock.attach_mock(targetfourth, "targetfourth")

        self._builder.run()

        manager_mock.assert_has_calls([
            call.targetfirst.do_completion_test(),
            call.targetfirst.do_build(),
            call.targetsecond.do_completion_test(),
            call.targetsecond.do_build(),
            call.targetthird.do_completion_test(),
            call.targetthird.do_build(),
            call.targetfourth.do_completion_test(),
            call.targetfourth.do_build()
        ], any_order=False)

    def test_targets_stop_running_on_error(self):
        target1 = self.addTarget()
        target2 = self.addTarget()
        target3 = self.addTarget()
        target4_raise_exc = self.addTarget(do_build_effect=BuildException(""))
        target5 = self.addTarget()
        target6 = self.addTarget()

        self._builder.run()

        target1.do_build.assert_called_once()
        target2.do_build.assert_called_once()
        target3.do_build.assert_called_once()
        target4_raise_exc.do_build.assert_called_once()
        target5.do_build.assert_not_called()
        target6.do_build.assert_not_called()

    def test_cleans_on_error_on_runs_for_targets_that_ran(self):
        target1 = self.addTarget()
        target2 = self.addTarget()
        target3_already_run = self.addTarget(do_completion_return=True)
        target4_raise_exc = self.addTarget(do_build_effect=BuildException(""))
        target5 = self.addTarget()
        target6 = self.addTarget()

        self._builder.run()

        target1.do_cleanup.assert_called_once()
        target2.do_cleanup.assert_called_once()
        target3_already_run.do_cleanuo.assert_not_called()
        target4_raise_exc.do_cleanup.assert_called_once()
        target5.do_cleanup.assert_not_called()
        target6.do_cleanup.assert_not_called()

    def test_clean_runs_target_regardless_of_clean_on_error_or_already_run_status(self):
        target_already_run = self.addTarget(do_completion_return=True)
        target = self.addTarget(do_completion_return=False)

        self._builder = BuilderImpl(self._compiler_mock, clean_on_failure=False)

        self._builder.clean()

        target_already_run.do_cleanup.assert_called_once()
        target.do_cleanup.assert_called_once()

    def test_clean_runs_targets_in_reverse_order(self):
        target1 = self.addTarget()
        target2 = self.addTarget()
        target3 = self.addTarget()

        mock_manager = MagicMock()
        mock_manager.attach_mock(target1, "target1")
        mock_manager.attach_mock(target2, "target2")
        mock_manager.attach_mock(target3, "target3")

        self._builder.clean()

        mock_manager.assert_has_calls([
            call.target3.do_cleanup(),
            call.target2.do_cleanup(),
            call.target1.do_cleanup()
        ], any_order=False)

    # Not sure if this is really correct
    def test_cleanup_exceptions_swallowed(self):
        target1 = self.addTarget()
        target2 = self.addTarget(do_cleanup_effect=BuildException(""))
        target3 = self.addTarget()

        try:
            self._builder.clean()
        except BuildException:
            self.fail()

        target1.do_cleanup.assert_called_once()
        target2.do_cleanup.assert_called_once()
        target3.do_cleanup.assert_called_once()


if __name__ == '__main__':
    unittest.main()
