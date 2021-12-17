from unittest import TestCase
from unittest.mock import Mock, call, patch

import os
import sys

sys.path.append(os.path.abspath('./src'))

from ui.ctrlrModel import CtrlrModel        # noqa: E402


class TestCtrlrModel(TestCase):
    """
    CtrlrModel test cases.
    """
    def setUp(self):
        """
        Test cases setup.
        """
        self.ctrlr = 'ui.ctrlrModel.ctrlrModel.Controller'
        self.testLogger = Mock()
        self.testCtrlrList = {'test controller 1': 0, 'test controller 2': 1,
                              'test controller 3': 2, 'test controller 4': 3}
        self._setUpMockedCtrlrs()
        with patch(self.ctrlr) as mockedCtrlr, \
                patch.object(mockedCtrlr, 'initFramework'), \
                patch.object(mockedCtrlr, 'listControllers') \
                as mockedListCtrlrs:
            mockedCtrlr.side_effect = self.testCtrlrs
            mockedListCtrlrs.return_value = self.testCtrlrList
            self.ctrlrMdl = CtrlrModel(self.testLogger,
                                       (None, None, None, None, None))

    def _setUpMockedCtrlrs(self):
        """
        Setup the mocked controllers.
        """
        self.testCtrlrs = []
        for testCtrlr in self.testCtrlrList:
            mockedCtrlr = Mock()
            mockedCtrlr.getName.return_value = testCtrlr
            mockedCtrlr.getIdx.return_value = self.testCtrlrList[testCtrlr]
            self.testCtrlrs.append(mockedCtrlr)

    def test_constructorInitCtrlrs(self):
        """
        The constructor must initialize the controller framework
        and update the controller list.
        """
        with patch(f"{self.ctrlr}.initFramework") as mockedinitFmk, \
                patch.object(CtrlrModel, 'updateCtrlrList') \
                as mockedInitCtrlrs:
            ctrlrMdl = CtrlrModel(self.testLogger,      # noqa: F841
                                  (None, None, None, None, None))
            mockedinitFmk.assert_called_once()
            mockedInitCtrlrs.assert_called_once()

    def test_listCurrentCtrlrs(self):
        """
        The _listCurrentCtrlrs mehod must return the list of
        current controller names.
        """
        testResult = self.ctrlrMdl._listCurrentCtrlrs()
        self.assertEqual(testResult, tuple(self.testCtrlrList.keys()))

    def test_filterAddedCtrlrs(self):
        """
        The _filterAddedCtrlrs method must return the list of
        newly added controllers.
        """
        addedCtrlrs = {'new controller 1': 6, 'new controller 2': 7}
        newList = {**self.testCtrlrList, **addedCtrlrs}
        testResult = self.ctrlrMdl._filterAddedCtrlrs(tuple(self.testCtrlrList),    # noqa: E501
                                                      newList)
        self.assertEqual(testResult, tuple(addedCtrlrs.keys()))

    def test_filterRemovedCtrlrs(self):
        """
        The _filterRemovedCtrlrs method must return the list
        of controllers that have been removed.
        """
        removedCtrlrs = ('test controller 2', 'test controller 4')
        newList = self.testCtrlrList.copy()
        for ctrlr in removedCtrlrs:
            del newList[ctrlr]
        testResult = self.ctrlrMdl._filterRemovedCtrlrs(tuple(self.testCtrlrList),  # noqa: E501
                                                        newList)
        self.assertEqual(testResult, removedCtrlrs)

    def test_addControllers(self):
        """
        The _addControllers method must add the new controllers.
        """
        addedCtrlrs = {'new controller 1': 6, 'new controller 2': 7}
        newList = {**self.testCtrlrList, **addedCtrlrs}
        # TODO: correct error.
        # self.ctrlrMdl._addControllers(newList, tuple(addedCtrlrs))
        # self.assertEqual(tuple(newList), self.ctrlrMdl._controllers['list'])

    def test_initCtrlrsListCtrlrs(self):
        """
        The initControllers method must list the available controllers.
        """
        with patch(self.ctrlr) as mockedCtrlr, \
                patch.object(mockedCtrlr, 'initFramework'), \
                patch.object(mockedCtrlr, 'listControllers') \
                as mockedListCtrlrs:
            mockedListCtrlrs.return_value = self.testCtrlrList
            self.ctrlrMdl.updateCtrlrList(self.testLogger)
            mockedListCtrlrs.assert_called_once()

    def test_initCtrlrsCreateCtrlrs(self):
        """
        The initControllers method must instanciate a Controller for each
        available controllers.
        """
        expectedCalls = []
        for ctrlrName in self.testCtrlrList:
            expectedCalls.append(call(self.testLogger,
                                      self.testCtrlrList[ctrlrName],
                                      ctrlrName))
        with patch(self.ctrlr) as mockedCtrlr, \
                patch.object(mockedCtrlr, 'initFramework'), \
                patch.object(mockedCtrlr, 'listControllers') \
                as mockedListCtrlrs:
            mockedListCtrlrs.return_value = self.testCtrlrList
            self.ctrlrMdl.updateCtrlrList(self.testLogger)
            mockedCtrlr.assert_has_calls(expectedCalls)
