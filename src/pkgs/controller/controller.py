import json
import os

import pygame as pg
from pygame import event, joystick


class Controller:
    """
    Class implementing the controller function.
    """
    CONFIG_ROOT_DIR = './src/pkgs/controller/configs/'
    TYPE_KEY = 'type'
    CTRLS_KEY = 'controls'
    AXES_KEY = 'axes'
    BTNS_KEY = 'buttons'
    HATS_KEY = 'hats'
    FUNC_KEY = 'functions'
    STRG_KEY = 'steering'
    THRTL_KEY = 'throttle'
    BRK_KEY = 'brake'
    RVS_KEY = 'reverse'
    CAL_SEQ = 6

    def __init__(self, logger: object, idx: int,
                 name: str, ndigit: int = 2) -> None:
        """
        Constructor.

        Params:
            dispatcher:     The application event dispatcher.
            logger:         The application logger.
            idx:            The index of the controller from 0 to
                            pygame.joystick.get_count().
            name:           The controller name.
            ndigit:         The digit number for the axis precision.
                            Default: 2.
        """
        self._logger = logger.getLogger(f"CTRL_{idx}")
        self._idx = idx
        self._ndigit = ndigit
        self._isCalibrated = False
        self._logger.info(f"creating controller {name}")
        self._joystick = joystick.Joystick(idx)
        self._joystick.init()
        filename = f"{name.lower().replace(' ', '_')}.json"
        configFilePath = os.path.join(self.CONFIG_ROOT_DIR, filename)
        with open(configFilePath) as configFile:
            self._config = json.load(configFile)

    @classmethod
    def initFramework(cls):
        """
        Initialize the pygame framework.
        """
        pg.init()
        pg.event.set_allowed([pg.JOYAXISMOTION, pg.JOYBUTTONDOWN,
                              pg.JOYBUTTONUP, pg.JOYHATMOTION])

    @classmethod
    def _listConnected(cls) -> tuple:
        """
        List the connected controller.

        Params:
            logger:     The logger.

        Returns:
            The list of connected controller.
        """
        connected = []
        for ctrlrId in range(joystick.get_count()):
            ctrlrName = joystick.Joystick(ctrlrId).get_name()
            connected.append(ctrlrName)
        return tuple(connected)

    @classmethod
    def _filterUnsupported(cls, connected: tuple, supported: tuple) -> dict:
        """
        Filter the unsupported controller.

        Params:
            connected:  The list of connected controller.
            supported:  The list of supported controller.

        Return:
            A dictionary listing the filtered controllers
        """
        filteredCtrlrs = {}
        for idx, ctrlrName in enumerate(connected):
            if any(ctrlrName.lower().replace(' ', '_')
                   in suppCtrlr for suppCtrlr in supported):
                filteredCtrlrs[connected[idx]] = idx
        return filteredCtrlrs

    @classmethod
    def listControllers(cls) -> dict:
        """
        List the connected and supported controller.

        Return:
            A Dictionary listing the connected and supported controller.
            The keys is the controller name and the value is its index.
        """
        connected = cls._listConnected()
        supported = (f.replace('.json', '')
                     for f in os.listdir(cls.CONFIG_ROOT_DIR))
        connected_supported = cls._filterUnsupported(connected,
                                                     tuple(supported))
        return connected_supported

    def _saveSteeringLeft(self) -> None:
        """
        Save the left position of the steering.
        """
        fullLeftSteering = \
            self._joystick.get_axis(self._getAxesMap().index(self.STRG_KEY))
        self._steeringLeft = abs(fullLeftSteering)
        self._logger.debug(f"saving steering left position as "
                           f"{self._steeringLeft}")

    def _saveSteeringRight(self) -> None:
        """
        Save the right position of the steering.
        """
        fullRightSteering = \
            self._joystick.get_axis(self._getAxesMap().index(self.STRG_KEY))
        self._steeringRight = abs(fullRightSteering)
        self._logger.debug(f"saving steering left position as "
                           f"{self._steeringRight}")

    def _saveThrottleOff(self) -> None:
        """
        Save the throttle off position.
        """
        throttleOff = \
            self._joystick.get_axis(self._getAxesMap().index(self.THRTL_KEY))
        self._throttleOff = abs(throttleOff)
        self._logger.debug(f"saving throttle off position as "
                           f"{self._throttleOff}")

    def _saveThrottleFull(self) -> None:
        """
        Save the throttle full position.
        """
        throttleFull = \
            self._joystick.get_axis(self._getAxesMap().index(self.THRTL_KEY))
        self._throttleFull = abs(throttleFull)
        self._logger.debug(f"saving throttle full position as "
                           f"{self._throttleFull}")

    def _saveBrakeOff(self) -> None:
        """
        Save the break off position.
        """
        brakeOff = \
            self._joystick.get_axis(self._getAxesMap().index(self.BRK_KEY))
        self._brakeOff = abs(brakeOff)
        self._logger.debug(f"saving break off position as {self._brakeOff}")

    def _saveBrakeFull(self) -> None:
        """
        Save the break full position.
        """
        brakeFull = \
            self._joystick.get_axis(self._getAxesMap().index(self.BRK_KEY))
        self._brakeFull = abs(brakeFull)
        self._logger.debug(f"saving break full position as {self._brakeFull}")

    def _getAxesMap(self) -> list:
        """
        Get the controller axis mapping.

        Return:
            The list containing the map of the axis.
        """
        return self._config[self.CTRLS_KEY][self.AXES_KEY]

    def _getButtonsMap(self) -> list:
        """
        Get the controller buttons mapping.

        Return:
            The list containing the map of the buttons.
        """
        return self._config[self.CTRLS_KEY][self.BTNS_KEY]

    def _getHatsMap(self) -> list:
        """
        Get the controller hats mapping.

        Return:
            The list containing the map of the hats.
        """
        return self._config[self.CTRLS_KEY][self.HATS_KEY]

    def _getFuncMap(self) -> dict:
        """
        Get the controller function mapping.

        Return:
            A dictionary containing the map of the functions.
        """
        return self._config[self.FUNC_KEY]

    def _getSteeringModifier(self) -> float:
        """
        Get the steering modifier.

        Return:
            The steering modifier.
        """
        axisName = self._getFuncMap()[self.STRG_KEY]
        steeringPos = \
            self._joystick.get_axis(self._getAxesMap().index(axisName))
        modifier = 0
        if steeringPos < 0:
            modifier = round(steeringPos / self._steeringLeft, self._ndigit)
        else:
            modifier = round(steeringPos / self._steeringRight, self._ndigit)
        self._logger.debug(f"steering modifier: {modifier}")
        return modifier

    def _getThrottleModifier(self) -> float:
        """
        Get the throttle modifier.

        Return:
            The throttle modifier.
        """
        axisName = self._getFuncMap()[self.THRTL_KEY]
        throttlePos = \
            self._joystick.get_axis(self._getAxesMap().index(axisName))
        tmpVal = self._throttleOff - throttlePos
        throttleRange = self._throttleOff - self._throttleFull
        modifier = round(tmpVal / throttleRange, self._ndigit)
        self._logger.debug(f"throttle modifier: {modifier}")
        return modifier

    def _getBrakeModifier(self) -> float:
        """
        Get the break modifier.

        Return:
            The break modifier.
        """
        axisName = self._getFuncMap()[self.BRK_KEY]
        brakePos = \
            self._joystick.get_axis(self._getAxesMap().index(axisName))
        tmpVal = self._brakeOff - brakePos
        brakeRange = self._brakeOff - self._brakeFull
        modifier = round(tmpVal / brakeRange, self._ndigit)
        self._logger.debug(f"break modifier: {modifier}")
        return modifier

    def _calibrate(self, calibSeqNumber: int) -> None:
        """
        Calibrate the controller.

        Params:
            calibSeqNumber: calibration sequence number.
        """
        calibrationSeq = [
            self._saveSteeringLeft,
            self._saveSteeringRight,
            self._saveThrottleOff,
            self._saveThrottleFull,
            self._saveBrakeOff,
            self._saveBrakeFull
        ]
        self._logger.info(f"calibration seq: {calibSeqNumber}.")
        calibrationSeq[calibSeqNumber]()
        if calibSeqNumber == self.CAL_SEQ - 1:
            self._isCalibrated = True

    def getName(self) -> str:
        """
        Get the joystick name.

        Return:
            The name of the controller.
        """
        return self._joystick.get_name()

    def getIdx(self) -> int:
        """
        Get the joystick index
        Return:
            The index of the controller.
        """
        return self._idx

    def getType(self) -> str:
        """
        Get the controller type.

        Return:
            The controller type.
        """
        return self._config[self.TYPE_KEY]

    def processEvents(self):
        """
        Process the controller events.
        """
        if self._isCalibrated:
            for ev in event.get():
                if event.type == pg.JOYAXISMOTION:
                    self._logger.debug(f"processing joystick "
                                       "{event.instance_id} "
                                       f"axis {event.axis} with "
                                       f"value {event.value}")
                    self._process_axis(event.instance_id, event.axis)
                if event.type == pg.JOYBUTTONDOWN:
                    self._logger.debug(f"processing joystick "
                                       "{event.instance_id} "
                                       f"button {event.button} down")
                    self._processButtonDown(event.instance_id, event.button)
                if event.type == pg.JOYBUTTONUP:
                    self._logger.debug(f"processing joystick "
                                       "{event.instance_id} "
                                       f"button {event.button} up")
                if event.type == pg.JOYHATMOTION:
                    self._logger.debug(f"processing joystick "
                                       "{event.instance_id} "
                                       f"hat {event.hat} with value "
                                       f"{event.value}")

    def quit(self) -> None:
        """
        Uninitialize the controller.
        """
        self._logger.info('unitializing controller')
        self._joystick.quit()
